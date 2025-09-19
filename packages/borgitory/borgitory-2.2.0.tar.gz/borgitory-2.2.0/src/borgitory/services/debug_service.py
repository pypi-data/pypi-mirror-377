import asyncio
import platform
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from borgitory.models.database import Repository, Job
from borgitory.services.jobs.job_manager import JobManager

logger = logging.getLogger(__name__)


class DebugService:
    """Service to gather system and application debug information"""

    def __init__(
        self, volume_service: Any = None, job_manager: Optional[JobManager] = None
    ) -> None:
        self.volume_service = volume_service
        self.job_manager = job_manager

    async def get_debug_info(self, db: Session) -> Dict[str, Any]:
        """Gather comprehensive debug information"""
        debug_info = {}

        # Get each section separately to avoid one failure breaking everything
        try:
            debug_info["system"] = await self._get_system_info()
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            debug_info["system"] = {"error": str(e)}

        try:
            debug_info["application"] = await self._get_application_info()
        except Exception as e:
            logger.error(f"Error getting application info: {str(e)}")
            debug_info["application"] = {"error": str(e)}

        try:
            debug_info["database"] = self._get_database_info(db)
        except Exception as e:
            logger.error(f"Error getting database info: {str(e)}")
            debug_info["database"] = {"error": str(e)}

        try:
            debug_info["volumes"] = await self._get_volume_info()
        except Exception as e:
            logger.error(f"Error getting volume info: {str(e)}")
            debug_info["volumes"] = {"error": str(e)}

        try:
            debug_info["tools"] = await self._get_tool_versions()
        except Exception as e:
            logger.error(f"Error getting tool versions: {str(e)}")
            debug_info["tools"] = {"error": str(e)}

        try:
            debug_info["environment"] = self._get_environment_info()
        except Exception as e:
            logger.error(f"Error getting environment info: {str(e)}")
            debug_info["environment"] = {"error": str(e)}

        try:
            debug_info["job_manager"] = self._get_job_manager_info()
        except Exception as e:
            logger.error(f"Error getting job manager info: {str(e)}")
            debug_info["job_manager"] = {"error": str(e)}

        return debug_info

    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": sys.version,
            "python_executable": sys.executable,
        }

    async def _get_application_info(self) -> Dict[str, Any]:
        """Get application information"""

        return {
            "borgitory_version": os.getenv("BORGITORY_VERSION"),
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
            "startup_time": datetime.now().isoformat(),
            "working_directory": os.getcwd(),
        }

    def _get_database_info(self, db: Session) -> Dict[str, Any]:
        """Get database information"""
        try:
            from borgitory.config import DATABASE_URL

            repository_count = db.query(Repository).count()
            total_jobs = db.query(Job).count()
            # Use started_at instead of created_at for Job model
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            recent_jobs = db.query(Job).filter(Job.started_at >= today_start).count()

            # Get database file size (for SQLite)
            database_size = "Unknown"
            database_size_bytes = 0
            try:
                if DATABASE_URL.startswith("sqlite:///"):
                    # Extract file path from SQLite URL (sqlite:///path/to/file.db)
                    db_path = DATABASE_URL[10:]  # Remove "sqlite:///" prefix
                    if os.path.exists(db_path):
                        database_size_bytes = os.path.getsize(db_path)
                        # Convert to human readable format
                        if database_size_bytes < 1024:
                            database_size = f"{database_size_bytes} B"
                        elif database_size_bytes < 1024 * 1024:
                            database_size = f"{database_size_bytes / 1024:.1f} KB"
                        elif database_size_bytes < 1024 * 1024 * 1024:
                            database_size = (
                                f"{database_size_bytes / (1024 * 1024):.1f} MB"
                            )
                        else:
                            database_size = (
                                f"{database_size_bytes / (1024 * 1024 * 1024):.1f} GB"
                            )
                    else:
                        database_size = f"File not found: {db_path}"
                elif DATABASE_URL.startswith("sqlite://"):
                    # Handle relative path format (sqlite://path/to/file.db)
                    db_path = DATABASE_URL[9:]  # Remove "sqlite://" prefix
                    if os.path.exists(db_path):
                        database_size_bytes = os.path.getsize(db_path)
                        # Convert to human readable format
                        if database_size_bytes < 1024:
                            database_size = f"{database_size_bytes} B"
                        elif database_size_bytes < 1024 * 1024:
                            database_size = f"{database_size_bytes / 1024:.1f} KB"
                        elif database_size_bytes < 1024 * 1024 * 1024:
                            database_size = (
                                f"{database_size_bytes / (1024 * 1024):.1f} MB"
                            )
                        else:
                            database_size = (
                                f"{database_size_bytes / (1024 * 1024 * 1024):.1f} GB"
                            )
                    else:
                        database_size = f"File not found: {db_path}"
            except Exception as size_error:
                database_size = f"Error: {str(size_error)}"

            return {
                "repository_count": repository_count,
                "total_jobs": total_jobs,
                "jobs_today": recent_jobs,
                "database_type": "SQLite",
                "database_url": DATABASE_URL,
                "database_size": database_size,
                "database_size_bytes": database_size_bytes,
                "database_accessible": True,
            }
        except Exception as e:
            return {"error": str(e), "database_accessible": False}

    async def _get_volume_info(self) -> Dict[str, Any]:
        """Get volume mount information"""
        try:
            # Use the shared volume service for volume discovery
            if self.volume_service:
                volume_info = await self.volume_service.get_volume_info()
                mounted_volumes = volume_info.get("mounted_volumes", [])
            else:
                # Fallback: use direct import (for backward compatibility)
                from borgitory.dependencies import get_volume_service

                volume_service = get_volume_service()
                volume_info = await volume_service.get_volume_info()
                mounted_volumes = volume_info.get("mounted_volumes", [])

            return {
                "mounted_volumes": mounted_volumes,
                "total_mounted_volumes": len(mounted_volumes),
            }

        except Exception as e:
            return {
                "error": str(e),
                "mounted_volumes": [],
                "total_mounted_volumes": 0,
            }

    async def _get_tool_versions(self) -> Dict[str, Any]:
        """Get versions of external tools"""
        tools = {}

        try:
            process = await asyncio.create_subprocess_exec(
                "borg",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                tools["borg"] = {"version": stdout.decode().strip(), "accessible": True}
            else:
                tools["borg"] = {
                    "error": stderr.decode().strip() if stderr else "Command failed",
                    "accessible": False,
                }
        except Exception as e:
            tools["borg"] = {"error": str(e), "accessible": False}

        try:
            process = await asyncio.create_subprocess_exec(
                "rclone",
                "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                version_output = stdout.decode().strip()
                # Extract just the version line
                version_line = (
                    version_output.split("\n")[0] if version_output else "Unknown"
                )
                tools["rclone"] = {"version": version_line, "accessible": True}
            else:
                tools["rclone"] = {
                    "error": stderr.decode().strip() if stderr else "Not installed",
                    "accessible": False,
                }
        except Exception as e:
            tools["rclone"] = {"error": str(e), "accessible": False}

        try:
            process = await asyncio.create_subprocess_exec(
                "dpkg",
                "-l",
                "fuse3",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode().strip()
                # Parse dpkg output to get version
                lines = output.split("\n")
                for line in lines:
                    if line.startswith("ii") and "fuse3" in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            version = parts[2]
                            tools["fuse3"] = {
                                "version": f"fuse3 {version}",
                                "accessible": True,
                            }
                            break
                else:
                    tools["fuse3"] = {
                        "error": "Package info not found",
                        "accessible": False,
                    }
            else:
                tools["fuse3"] = {
                    "error": stderr.decode().strip()
                    if stderr
                    else "Package not installed",
                    "accessible": False,
                }
        except Exception as e:
            tools["fuse3"] = {"error": str(e), "accessible": False}

        try:
            process = await asyncio.create_subprocess_exec(
                "dpkg",
                "-l",
                "python3-pyfuse3",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode().strip()
                # Parse dpkg output to get version
                lines = output.split("\n")
                for line in lines:
                    if line.startswith("ii") and "python3-pyfuse3" in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            version = parts[2]
                            tools["python3-pyfuse3"] = {
                                "version": f"python3-pyfuse3 {version}",
                                "accessible": True,
                            }
                            break
                else:
                    tools["python3-pyfuse3"] = {
                        "error": "Package info not found",
                        "accessible": False,
                    }
            else:
                tools["python3-pyfuse3"] = {
                    "error": stderr.decode().strip()
                    if stderr
                    else "Package not installed",
                    "accessible": False,
                }
        except Exception as e:
            tools["python3-pyfuse3"] = {"error": str(e), "accessible": False}

        return tools

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment variables (sanitized)"""
        env_info = {}

        # List of environment variables that are safe to display
        safe_env_vars = [
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "LANG",
            "LC_ALL",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "CONDA_DEFAULT_ENV",
            "DATABASE_URL",
            "DEBUG",
        ]

        for var in safe_env_vars:
            value = os.environ.get(var)
            if value:
                # Sanitize sensitive information
                if (
                    "PASSWORD" in var.upper()
                    or "SECRET" in var.upper()
                    or "KEY" in var.upper()
                ):
                    env_info[var] = "***HIDDEN***"
                elif var == "DATABASE_URL" and "sqlite" not in value.lower():
                    # Hide connection details for non-sqlite databases
                    env_info[var] = "***HIDDEN***"
                else:
                    env_info[var] = value

        return env_info

    def _get_job_manager_info(self) -> Dict[str, Any]:
        """Get job manager information"""
        try:
            if not self.job_manager:
                # Return minimal info if no job manager injected
                return {
                    "status": "No job manager available",
                    "active_jobs": 0,
                    "total_jobs": 0,
                }

            # Count active jobs by checking job statuses
            active_jobs_count = 0
            total_jobs = (
                len(self.job_manager.jobs) if hasattr(self.job_manager, "jobs") else 0
            )

            if hasattr(self.job_manager, "jobs"):
                for job in self.job_manager.jobs.values():
                    if hasattr(job, "status") and job.status == "running":
                        active_jobs_count += 1

            return {
                "active_jobs": active_jobs_count,
                "total_jobs": total_jobs,
                "job_manager_running": True,
            }
        except Exception as e:
            return {"error": str(e), "job_manager_running": False}
