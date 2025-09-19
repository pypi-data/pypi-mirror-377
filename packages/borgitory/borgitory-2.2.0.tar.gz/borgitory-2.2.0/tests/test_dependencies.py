"""
Tests for FastAPI dependency providers
"""

from borgitory.dependencies import (
    get_simple_command_runner,
    get_borg_service,
    get_job_service,
    get_recovery_service,
    get_pushover_service,
    get_job_stream_service,
    get_job_render_service,
    get_debug_service,
    get_rclone_service,
    get_repository_stats_service,
    get_volume_service,
)
from borgitory.services.simple_command_runner import SimpleCommandRunner
from borgitory.services.borg_service import BorgService
from borgitory.services.jobs.job_service import JobService
from borgitory.services.recovery_service import RecoveryService
from borgitory.services.notifications.pushover_service import PushoverService
from borgitory.services.jobs.job_stream_service import JobStreamService
from borgitory.services.jobs.job_render_service import JobRenderService
from borgitory.services.debug_service import DebugService
from borgitory.services.rclone_service import RcloneService
from borgitory.services.repositories.repository_stats_service import (
    RepositoryStatsService,
)
from borgitory.services.volumes.volume_service import VolumeService


class TestDependencies:
    """Test class for dependency providers."""

    def test_get_simple_command_runner(self) -> None:
        """Test SimpleCommandRunner dependency provider."""
        runner = get_simple_command_runner()

        assert isinstance(runner, SimpleCommandRunner)
        assert runner.timeout == 300  # Default timeout

        # Should return same instance due to singleton pattern
        runner2 = get_simple_command_runner()
        assert runner is runner2

    def test_get_borg_service(self) -> None:
        """Test BorgService dependency provider."""
        service = get_borg_service()

        assert isinstance(service, BorgService)
        assert isinstance(service.command_runner, SimpleCommandRunner)

        # Should return same instance due to singleton pattern
        service2 = get_borg_service()
        assert service is service2

    def test_borg_service_has_injected_command_runner(self) -> None:
        """Test that BorgService receives the proper command runner dependency."""
        service = get_borg_service()
        command_runner = get_simple_command_runner()

        # The command runner should be the same instance (singleton pattern)
        assert service.command_runner is command_runner

    def test_borg_service_has_injected_volume_service(self) -> None:
        """Test that BorgService receives the proper volume service dependency."""
        service = get_borg_service()
        volume_service = get_volume_service()

        # The volume service should be the same instance (singleton pattern)
        assert service.volume_service is volume_service

    def test_dependency_isolation_in_tests(self) -> None:
        """Test that dependencies can be properly mocked in tests."""
        from unittest.mock import Mock

        # This demonstrates how to inject mock dependencies for testing
        mock_runner = Mock(spec=SimpleCommandRunner)
        service = BorgService(command_runner=mock_runner)

        assert service.command_runner is mock_runner
        assert isinstance(mock_runner, Mock)

    def test_get_job_service(self) -> None:
        """Test JobService dependency provider."""
        service = get_job_service()

        assert isinstance(service, JobService)

        # JobService creates new instances per request (not singleton)
        service2 = get_job_service()
        assert service is not service2  # Different instances
        assert isinstance(service2, JobService)

    def test_get_recovery_service(self) -> None:
        """Test RecoveryService dependency provider."""
        service = get_recovery_service()

        assert isinstance(service, RecoveryService)

        # Should return same instance due to singleton pattern
        service2 = get_recovery_service()
        assert service is service2

    def test_get_pushover_service(self) -> None:
        """Test PushoverService dependency provider."""
        service = get_pushover_service()

        assert isinstance(service, PushoverService)

        # Should return same instance due to singleton pattern
        service2 = get_pushover_service()
        assert service is service2

    def test_get_job_stream_service(self) -> None:
        """Test JobStreamService dependency provider."""
        service = get_job_stream_service()

        assert isinstance(service, JobStreamService)

        # Should return same instance due to singleton pattern
        service2 = get_job_stream_service()
        assert service is service2

    def test_get_job_render_service(self) -> None:
        """Test JobRenderService dependency provider."""
        service = get_job_render_service()

        assert isinstance(service, JobRenderService)

        # Should return same instance due to singleton pattern
        service2 = get_job_render_service()
        assert service is service2

    def test_get_debug_service(self) -> None:
        """Test DebugService dependency provider."""
        service = get_debug_service()

        assert isinstance(service, DebugService)

        # Should return same instance due to singleton pattern
        service2 = get_debug_service()
        assert service is service2

    def test_debug_service_has_injected_volume_service(self) -> None:
        """Test that DebugService receives the proper volume service dependency."""
        service = get_debug_service()
        volume_service = get_volume_service()

        # The volume service should be the same instance (singleton pattern)
        assert service.volume_service is volume_service

    def test_get_rclone_service(self) -> None:
        """Test RcloneService dependency provider."""
        service = get_rclone_service()

        assert isinstance(service, RcloneService)

        # Should return same instance due to singleton pattern
        service2 = get_rclone_service()
        assert service is service2

    def test_get_repository_stats_service(self) -> None:
        """Test RepositoryStatsService dependency provider."""
        service = get_repository_stats_service()

        assert isinstance(service, RepositoryStatsService)

        # Should return same instance due to singleton pattern
        service2 = get_repository_stats_service()
        assert service is service2

    def test_get_volume_service(self) -> None:
        """Test VolumeService dependency provider."""
        service = get_volume_service()

        assert isinstance(service, VolumeService)

        # Should return same instance due to singleton pattern
        service2 = get_volume_service()
        assert service is service2

    def test_default_initialization_still_works(self) -> None:
        """Test that services can still be initialized without dependency injection."""
        from unittest.mock import Mock

        # This ensures backward compatibility
        runner = SimpleCommandRunner()
        service = BorgService()
        mock_db = Mock()  # JobService now requires a database session
        mock_job_manager = Mock()
        job_service = JobService(db=mock_db, job_manager=mock_job_manager)
        recovery_service = RecoveryService()
        pushover_service = PushoverService()
        job_stream_service = JobStreamService(mock_job_manager)
        job_render_service = JobRenderService(job_manager=mock_job_manager)
        debug_service = DebugService()
        rclone_service = RcloneService()
        repository_stats_service = RepositoryStatsService()

        assert isinstance(runner, SimpleCommandRunner)
        assert isinstance(service, BorgService)
        assert isinstance(job_service, JobService)
        assert isinstance(recovery_service, RecoveryService)
        assert isinstance(pushover_service, PushoverService)
        assert isinstance(job_stream_service, JobStreamService)
        assert isinstance(job_render_service, JobRenderService)
        assert isinstance(debug_service, DebugService)
        assert isinstance(rclone_service, RcloneService)
        assert isinstance(repository_stats_service, RepositoryStatsService)
        assert isinstance(service.command_runner, SimpleCommandRunner)

        # These should be different instances (not singletons)
        service2 = BorgService()
        assert service.command_runner is not service2.command_runner
