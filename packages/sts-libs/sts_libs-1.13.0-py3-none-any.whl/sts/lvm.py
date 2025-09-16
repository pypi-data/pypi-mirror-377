# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""LVM device management.

This module provides functionality for managing LVM devices:
- Physical Volume (PV) operations
- Volume Group (VG) operations
- Logical Volume (LV) operations

LVM (Logical Volume Management) provides flexible disk space management:
1. Physical Volumes (PVs): Physical disks or partitions
2. Volume Groups (VGs): Pool of space from PVs
3. Logical Volumes (LVs): Virtual partitions from VG space

Key benefits:
- Resize filesystems online
- Snapshot and mirror volumes
- Stripe across multiple disks
- Move data between disks
"""

from __future__ import annotations

import logging
import re
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, TypedDict

from sts.base import StorageDevice
from sts.udevadm import udevadm_settle
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


class LvmOptions(TypedDict, total=False):
    """LVM command options.

    Common options:
    - size: Volume size (e.g. '1G', '500M')
    - extents: Volume size in extents (e.g. '100%FREE')
    - permission: Volume permission (rw/r)
    - persistent: Make settings persistent across reboots
    - monitor: Monitor volume for events
    - autobackup: Auto backup metadata after changes

    Size can be specified in:
    - Absolute size (1G, 500M)
    - Percentage of VG (80%VG)
    - Percentage of free space (100%FREE)
    - Physical extents (100)
    """

    size: str
    extents: str
    permission: str
    persistent: str
    monitor: str
    autobackup: str


@dataclass
class PVInfo:
    """Physical Volume information.

    Stores key information about a Physical Volume:
    - Volume group membership
    - Format type (lvm2)
    - Attributes (allocatable, exported, etc)
    - Size information (total and free space)

    Args:
        vg: Volume group name (None if not in a VG)
        fmt: PV format (usually 'lvm2')
        attr: PV attributes (e.g. 'a--' for allocatable)
        psize: PV size (e.g. '1.00t')
        pfree: PV free space (e.g. '500.00g')
    """

    vg: str | None
    fmt: str
    attr: str
    psize: str
    pfree: str


@dataclass
class LvmDevice(StorageDevice):
    """Base class for LVM devices.

    Provides common functionality for all LVM device types:
    - Command execution with standard options
    - Configuration management
    - Basic device operations

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation

    The yes and force options are useful for automation:
    - yes: Skip interactive prompts
    - force: Ignore warnings and errors
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None
    validate_on_init = False

    # Optional parameters for this class
    yes: bool = True  # Answer yes to prompts
    force: bool = False  # Force operations

    # Internal fields
    _config_path: Path = field(init=False, default=Path('/etc/lvm/lvm.conf'))

    def __post_init__(self) -> None:
        """Initialize LVM device."""
        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Initialize parent class
        super().__post_init__()

    def _run(self, cmd: str, *args: str | Path | None, **kwargs: str) -> CommandResult:
        """Run LVM command.

        Builds and executes LVM commands with standard options:
        - Adds --yes for non-interactive mode
        - Adds --force to ignore warnings
        - Converts Python parameters to LVM options

        Args:
            cmd: Command name (e.g. 'pvcreate')
            *args: Command arguments
            **kwargs: Command parameters

        Returns:
            Command result
        """
        command = [cmd]
        if self.yes:
            command.append('--yes')
        if self.force:
            command.append('--force')
        if args:
            command.extend(str(arg) for arg in args if arg)
        if kwargs:
            command.extend(f'--{k.replace("_", "-")}={v}' for k, v in kwargs.items() if v)

        return run(' '.join(command))

    @abstractmethod
    def create(self, **options: str) -> bool:
        """Create LVM device.

        Args:
            **options: Device options (see LvmOptions)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def remove(self, **options: str) -> bool:
        """Remove LVM device.

        Args:
            **options: Device options (see LvmOptions)

        Returns:
            True if successful, False otherwise
        """


@dataclass
class PhysicalVolume(LvmDevice):
    """Physical Volume device.

    A Physical Volume (PV) is a disk or partition used by LVM.
    PVs provide the storage pool for Volume Groups.

    Key features:
    - Initialize disks/partitions for LVM use
    - Track space allocation
    - Handle bad block management
    - Store LVM metadata

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        vg: Volume group name (optional, discovered from device)
        fmt: PV format (optional, discovered from device)
        attr: PV attributes (optional, discovered from device)
        pfree: PV free space (optional, discovered from device)

    Example:
        ```python
        pv = PhysicalVolume(name='sda1')  # Discovers other values
        pv = PhysicalVolume.create('/dev/sda1')  # Creates new PV
        ```
    """

    # Optional parameters for this class
    vg: str | None = None  # Volume Group membership
    fmt: str | None = None  # PV format (usually lvm2)
    attr: str | None = None  # PV attributes
    pfree: str | None = None  # Free space

    # Available PV commands
    COMMANDS: ClassVar[list[str]] = [
        'pvchange',  # Modify PV attributes
        'pvck',  # Check PV metadata
        'pvcreate',  # Initialize PV
        'pvdisplay',  # Show PV details
        'pvmove',  # Move PV data
        'pvremove',  # Remove PV
        'pvresize',  # Resize PV
        'pvs',  # List PVs
        'pvscan',  # Scan for PVs
    ]

    # Discover PV info if path is available
    def discover_pv_info(self) -> None:
        """Discovers PV information if path is available.

        Volume group membership.
        Format and attributes.
        Size information.
        """
        result = run(f'pvs {self.path} --noheadings --separator ","')
        if result.succeeded:
            # Parse PV info line
            # Format: PV,VG,Fmt,Attr,PSize,PFree
            parts = result.stdout.strip().split(',')
            if len(parts) == 6:
                _, vg, fmt, attr, _, pfree = parts
                if not self.vg:
                    self.vg = vg or None
                if not self.fmt:
                    self.fmt = fmt
                if not self.attr:
                    self.attr = attr
                if not self.pfree:
                    self.pfree = pfree

    def create(self, **options: str) -> bool:
        """Create Physical Volume.

        Initializes a disk or partition for use with LVM:
        - Creates LVM metadata area
        - Prepares device for VG membership

        Args:
            **options: PV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pv = PhysicalVolume(path='/dev/sda1')
            pv.create()
            True
            ```
        """
        if not self.path:
            logging.error('Device path required')
            return False

        result = self._run('pvcreate', str(self.path), **options)
        if result.succeeded:
            self.discover_pv_info()
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove Physical Volume.

        Removes LVM metadata from device:
        - Device must not be in use by a VG
        - Data on device is not erased

        Args:
            **options: PV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pv = PhysicalVolume(path='/dev/sda1')
            pv.remove()
            True
            ```
        """
        if not self.path:
            logging.error('Device path required')
            return False

        result = self._run('pvremove', str(self.path), **options)
        return result.succeeded

    @classmethod
    def get_all(cls) -> dict[str, PVInfo]:
        """Get all Physical Volumes.

        Returns:
            Dictionary mapping PV names to their information

        Example:
            ```python
            PhysicalVolume.get_all()
            {'/dev/sda1': PVInfo(vg='vg0', fmt='lvm2', ...)}
            ```
        """
        result = run('pvs --noheadings --separator ","')
        if result.failed:
            logging.debug('No Physical Volumes found')
            return {}

        # Format: PV,VG,Fmt,Attr,PSize,PFree
        pv_info_regex = r'\s+(\S+),(\S+)?,(\S+),(.*),(.*),(.*)$'
        pv_dict = {}

        for line in result.stdout.splitlines():
            if match := re.match(pv_info_regex, line):
                pv_dict[match.group(1)] = PVInfo(
                    vg=match.group(2) or None,  # VG can be empty
                    fmt=match.group(3),
                    attr=match.group(4),
                    psize=match.group(5),
                    pfree=match.group(6),
                )

        return pv_dict


@dataclass
class VolumeGroup(LvmDevice):
    """Volume Group device.

    A Volume Group (VG) combines Physical Volumes into a storage pool.
    This pool can then be divided into Logical Volumes.

    Key features:
    - Combine multiple PVs
    - Manage storage pool
    - Track extent allocation
    - Handle PV addition/removal

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        pvs: List of Physical Volumes (optional, discovered from device)

    Example:
        ```python
        vg = VolumeGroup(name='vg0')  # Discovers other values
        vg = VolumeGroup.create('vg0', ['/dev/sda1'])  # Creates new VG
        ```
    """

    # Optional parameters for this class
    pvs: list[str] = field(default_factory=list)  # Member PVs

    # Available VG commands
    COMMANDS: ClassVar[list[str]] = [
        'vgcfgbackup',  # Backup VG metadata
        'vgcfgrestore',  # Restore VG metadata
        'vgchange',  # Change VG attributes
        'vgck',  # Check VG metadata
        'vgconvert',  # Convert VG metadata format
        'vgcreate',  # Create VG
        'vgdisplay',  # Show VG details
        'vgexport',  # Make VG inactive
        'vgextend',  # Add PVs to VG
        'vgimport',  # Make VG active
        'vgimportclone',  # Import cloned PVs
        'vgimportdevices',  # Import PVs into VG
        'vgmerge',  # Merge VGs
        'vgmknodes',  # Create VG special files
        'vgreduce',  # Remove PVs from VG
        'vgremove',  # Remove VG
        'vgrename',  # Rename VG
        'vgs',  # List VGs
        'vgscan',  # Scan for VGs
        'vgsplit',  # Split VG into two
    ]

    def discover_pvs(self) -> list[str] | None:
        """Discover PVs if name is available."""
        if self.name:
            result = run(f'vgs {self.name} -o pv_name --noheadings')
            if result.succeeded:
                self.pvs = result.stdout.strip().splitlines()
                return self.pvs
        return None

    def create(self, **options: str) -> bool:
        """Create Volume Group.

        Creates a new VG from specified PVs:
        - Initializes VG metadata
        - Sets up extent allocation
        - Creates device mapper devices

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0', pvs=['/dev/sda1'])
            vg.create()
            True
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False
        if not self.pvs:
            logging.error('Physical volumes required')
            return False

        result = self._run('vgcreate', self.name, *self.pvs, **options)
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove Volume Group.

        Removes VG and its metadata:
        - All LVs must be removed first
        - PVs are released but not removed

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0')
            vg.remove()
            True
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False

        result = self._run('vgremove', self.name, **options)
        return result.succeeded


@dataclass
class LogicalVolume(LvmDevice):
    """Logical Volume device.

    A Logical Volume (LV) is a virtual partition created from VG space.
    LVs appear as block devices that can be formatted and mounted.

    Key features:
    - Flexible sizing
    - Online resizing
    - Snapshots
    - Striping and mirroring
    - Thin provisioning

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<vg>/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        vg: Volume group name (optional, discovered from device)

    Example:
        ```python
        lv = LogicalVolume(name='lv0')  # Discovers other values
        lv = LogicalVolume.create('lv0', 'vg0', size='1G')  # Creates new LV
        ```
    """

    # Optional parameters for this class
    vg: str | None = None  # Parent VG
    pool_name: str | None = None

    # Available LV commands
    COMMANDS: ClassVar[list[str]] = [
        'lvchange',  # Change LV attributes
        'lvcreate',  # Create LV
        'lvconvert',  # Convert LV type
        'lvdisplay',  # Show LV details
        'lvextend',  # Increase LV size
        'lvreduce',  # Reduce LV size
        'lvremove',  # Remove LV
        'lvrename',  # Rename LV
        'lvresize',  # Change LV size
        'lvs',  # List LVs
        'lvscan',  # Scan for LVs
    ]

    def __post_init__(self) -> None:
        """Initialize Logical Volume.

        - Sets device path from name and VG
        - Discovers VG membership
        """
        # Set path based on name and vg if not provided
        if not self.path and self.name and self.vg:
            self.path = f'/dev/{self.vg}/{self.name}'

    def discover_vg(self) -> str | None:
        """Discover VG if name is available."""
        if self.name and not self.vg:
            result = run(f'lvs {self.name} -o vg_name --noheadings')
            if result.succeeded:
                self.vg = result.stdout.strip()
                return self.vg
        return None

    def create(self, **options: str) -> bool:
        """Create Logical Volume.

        Creates a new LV in the specified VG:
        - Allocates space from VG
        - Creates device mapper device
        - Initializes LV metadata

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.create(size='1G')
            True
            ```
        """
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.vg:
            logging.error('Volume group required')
            return False

        result = self._run('lvcreate', '-n', self.name, self.vg, **options)
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove Logical Volume.

        Removes LV and its data:
        - Data is permanently lost
        - Space is returned to VG
        - Device mapper device is removed

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.remove()
            True
            ```
        """
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.vg:
            logging.error('Volume group required')
            return False

        result = self._run('lvremove', f'{self.vg}/{self.name}', **options)
        return result.succeeded

    def change(self, *args: str, **options: str) -> bool:
        """Create Logical Volume.

        Change a general LV attribute:

        Args:
            *args: LV options (see LVMOptions)
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.change('-an', 'vg0/lv0')
            True
            ```
        """
        result = self._run('lvchange', *args, **options)
        return result.succeeded

    def extend(self, **options: str) -> bool:
        """Extend Logical volume.

        - LV must be initialized (using lvcreate)
        - VG must have sufficient usable space

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lvol0', vg='vg0')
            lv.extend(extents='100%vg')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvextend', f'{self.vg}/{self.name}', **options)
        return result.succeeded

    def lvs(self, *args: str, **options: str) -> CommandResult:
        """Get information about logical volumes.

        Executes the 'lvs' command with optional filtering to display
        information about logical volumes.

        Args:
            *args: Positional args passed through to `lvs` (e.g., LV selector, flags).
            **options: LV command options (see LvmOptions).

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume()
            result = lv.lvs()
            print(result.stdout)
            ```
        """
        return self._run('lvs', *args, **options)

    def convert(self, *args: str, **options: str) -> bool:
        """Convert Logical Volume type.

        Converts LV type (linear, striped, mirror, snapshot, etc):
        - Can change between different LV types
        - May require additional space or devices
        - Some conversions are irreversible

        Args:
            *args: LV conversion arguments
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.convert('--type', 'mirror')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvconvert', f'{self.vg}/{self.name}', *args, **options)
        return result.succeeded

    def display(self, **options: str) -> CommandResult:
        """Display Logical Volume details.

        Shows detailed information about the LV:
        - Size and allocation
        - Attributes and permissions
        - Segment information
        - Device mapper details

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            result = lv.display()
            print(result.stdout)
            ```
        """
        if not self.vg or not self.name:
            return self._run('lvdisplay', **options)
        return self._run('lvdisplay', f'{self.vg}/{self.name}', **options)

    def reduce(self, **options: str) -> bool:
        """Reduce Logical Volume size.

        Reduces LV size (shrinks the volume):
        - Filesystem must be shrunk first
        - Data loss risk if not done carefully
        - Cannot reduce below used space

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.reduce(size='500M')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvreduce', f'{self.vg}/{self.name}', **options)
        return result.succeeded

    def rename(self, new_name: str, **options: str) -> bool:
        """Rename Logical Volume.

        Changes the LV name:
        - Must not conflict with existing LV names
        - Updates device mapper devices
        - May require remounting if mounted

        Args:
            new_name: New name for the LV
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.rename('new_lv')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not new_name:
            logging.error('New name required')
            return False

        result = self._run('lvrename', f'{self.vg}/{self.name}', new_name, **options)
        if result.succeeded:
            self.name = new_name
            self.path = f'/dev/{self.vg}/{self.name}'
        return result.succeeded

    def resize(self, **options: str) -> bool:
        """Resize Logical Volume.

        Changes LV size (can grow or shrink):
        - Combines extend and reduce functionality
        - Safer than lvreduce for shrinking
        - Can resize filesystem simultaneously

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.resize(size='2G')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvresize', f'{self.vg}/{self.name}', **options)
        return result.succeeded

    def scan(self, **options: str) -> CommandResult:
        """Scan for Logical Volumes.

        Scans all devices for LV information:
        - Discovers new LVs
        - Updates device mapper
        - Useful after system changes

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume()
            result = lv.scan()
            print(result.stdout)
            ```
        """
        return self._run('lvscan', **options)

    def deactivate(self) -> bool:
        """Deactivate Logical Volume."""
        udevadm_settle()
        result = self.change('-an', f'{self.vg}/{self.name}')
        if result:
            return self.wait_for_lv_deactivation()
        return result

    def activate(self) -> bool:
        """Activate Logical Volume."""
        return self.change('-ay', f'{self.vg}/{self.name}')

    def wait_for_lv_deactivation(self, timeout: int = 30) -> bool:
        """Wait for logical volume to be fully deactivated.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if deactivated successfully, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check LV status using lvs command
            result = self.lvs(f'{self.vg}/{self.name}', '--noheadings', '-o lv_active')
            if result.succeeded and 'active' not in result.stdout.lower():
                # LV is inactive - also verify device node is gone
                if self.path is not None:
                    device_path = Path(self.path)
                    if not device_path.exists():
                        return True
                else:
                    return True  # If no path, consider it deactivated
            time.sleep(2)  # Poll every 2 seconds

        logging.warning(f'LV {self.vg}/{self.name} deactivation timed out after {timeout}s')
        return False
