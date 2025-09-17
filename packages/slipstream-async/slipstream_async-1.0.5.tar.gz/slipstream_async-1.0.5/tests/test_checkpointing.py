"""Checkpointing tests."""

from datetime import datetime, timedelta, timezone

import pytest
from conftest import emoji, iterable_to_async

from slipstream.checkpointing import Checkpoint, Dependency
from slipstream.core import Conf, Signal

UTC = timezone.utc


@pytest.fixture
def dependency():
    """Dependency instance."""
    return Dependency('emoji', emoji())


@pytest.fixture
def checkpoint(mock_cache):
    """Checkpoint instance."""

    async def dependent():
        yield {
            'event_timestamp': datetime(2025, 1, 1, 10, tzinfo=UTC),
        }

    async def dependency():
        yield {
            'event_timestamp': datetime(2025, 1, 1, 10, tzinfo=UTC),
        }

    dep = Dependency('dependency', dependency())

    return Checkpoint('test', dependent(), [dep], cache=mock_cache)


def test_dependency_init(dependency):
    """Should properly initialize dependency."""
    assert dependency.name == 'emoji'
    assert dependency.checkpoint_state is None
    assert dependency.checkpoint_marker is None
    assert isinstance(dependency.downtime_threshold, timedelta)
    assert dependency.is_down is False


def test_dependency_save_and_load(mock_cache, dependency):
    """Should save and load dependency using cache."""
    checkpoint_state = {'offset': 1}
    checkpoint_marker = datetime(2025, 1, 1, 10, tzinfo=UTC)
    dependency.save(
        mock_cache,
        '_prefix_',
        checkpoint_state,
        checkpoint_marker,
    )

    loaded_dep = Dependency('emoji', iterable_to_async([]))
    loaded_dep.load(mock_cache, '_prefix_')

    assert loaded_dep.checkpoint_state == checkpoint_state
    assert loaded_dep.checkpoint_marker == checkpoint_marker


@pytest.mark.asyncio
async def test_default_downtime_check(dependency):
    """Should check for datetime diff surpassing threshold."""
    checkpoint = Checkpoint('test', iterable_to_async([]), [dependency])

    checkpoint.state_marker = 'not-datetime'
    dependency.checkpoint_marker = 'not-datetime'
    with pytest.raises(TypeError, match='Expecting either `datetime`'):
        dependency._default_downtime_check(checkpoint, dependency)

    checkpoint.state_marker = datetime(2025, 1, 1, 11, tzinfo=UTC)
    dependency.checkpoint_marker = datetime(2025, 1, 1, 10, tzinfo=UTC)
    downtime = dependency._default_downtime_check(checkpoint, dependency)
    assert isinstance(downtime, timedelta)
    assert downtime == timedelta(hours=1)


@pytest.mark.asyncio
async def test_default_recovery_check(dependency):
    """Should check surpassing datetime is true."""
    checkpoint = Checkpoint('test', iterable_to_async([]), [dependency])

    checkpoint.state_marker = 'not-datetime'
    dependency.checkpoint_marker = 'not-datetime'
    with pytest.raises(TypeError, match='Expecting either `datetime`'):
        dependency._default_recovery_check(checkpoint, dependency)

    checkpoint.state_marker = datetime(2025, 1, 1, 10, tzinfo=UTC)
    dependency.checkpoint_marker = datetime(2025, 1, 1, 11, tzinfo=UTC)
    recovered = dependency._default_recovery_check(checkpoint, dependency)
    assert recovered is True


def test_checkpoint_init(checkpoint):
    """Should properly initialize checkpoint."""
    assert checkpoint.name == 'test'
    assert isinstance(checkpoint.dependencies, dict)
    assert 'dependency' in checkpoint.dependencies
    assert checkpoint.state == {}
    assert checkpoint.state_marker is None


@pytest.mark.asyncio
async def test_heartbeat_single_dependency(checkpoint):
    """Should correctly update dependency data."""
    marker = datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
    await checkpoint.heartbeat(marker)

    with pytest.raises(KeyError):
        await checkpoint.heartbeat(marker, 'not-existing')

    dep = checkpoint['dependency']
    assert dep.checkpoint_marker == marker
    assert dep.checkpoint_state == checkpoint.state


@pytest.mark.asyncio
async def test_heartbeat_multiple_dependencies_error(checkpoint):
    """Should warn about missing argument."""
    checkpoint.dependencies['extra'] = Dependency(
        'extra',
        iterable_to_async([]),
    )
    with pytest.raises(ValueError, match='`dependency_name` must be provided'):
        await checkpoint.heartbeat(
            datetime(2025, 1, 1, 10, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_heartbeat_with_dependency_name(checkpoint):
    """Should correctly update dependency data."""
    checkpoint.dependencies['extra'] = Dependency(
        'extra',
        iterable_to_async([]),
    )
    marker = datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
    await checkpoint.heartbeat(marker, 'dependency')

    dep = checkpoint['dependency']
    assert dep.checkpoint_marker == marker
    assert checkpoint['extra'].checkpoint_marker is None


@pytest.mark.asyncio
async def test_check_pulse_initial_state(checkpoint):
    """Should update dependency and checkpoint data."""
    marker = datetime(2025, 1, 1, 10, tzinfo=UTC)
    await checkpoint.check_pulse(marker, offset=0)

    dep = checkpoint['dependency']
    assert dep.checkpoint_marker == marker
    assert dep.checkpoint_state == {'offset': 0}
    assert checkpoint.state_marker == marker


@pytest.mark.asyncio
async def test_check_pulse_downtime_detected(checkpoint, mocker):
    """Should detect downtime and pause dependent stream."""
    c = Conf()
    mock_iterable = mocker.MagicMock()
    dependent_key = str(id(checkpoint.dependent))
    c.register_iterable(dependent_key, mock_iterable)
    pausable_stream = c.iterables[dependent_key]
    assert pausable_stream.signal is None

    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 10, tzinfo=UTC),
        offset=0,
    )

    downtime = await checkpoint.check_pulse(
        datetime(2025, 1, 1, 10, 30, tzinfo=UTC),
        offset=1,
    )

    # Downtime observed, dependent paused
    assert isinstance(downtime, timedelta)
    assert checkpoint['dependency'].is_down is True
    assert pausable_stream.signal is Signal.PAUSE


@pytest.mark.asyncio
async def test_check_heartbeat_downtime_recovered(checkpoint, mocker):
    """Should detect recovery and resume dependent stream."""
    c = Conf()
    mock_iterable = mocker.MagicMock()
    dependent_key = str(id(checkpoint.dependent))
    c.register_iterable(dependent_key, mock_iterable)
    pausable_stream = c.iterables[dependent_key]
    assert pausable_stream.signal is None

    # If no dependency data has ever come in yet, use the first
    # pulse as a checkpoint_marker
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 10, tzinfo=UTC),
        offset=0,
    )
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 11, tzinfo=UTC),
        offset=1,
    )

    # Even though no dependency data has come in yet, it's already
    # marked as down using the fact that the dependent stream has
    # processed one hour of data
    assert checkpoint['dependency'].is_down is True
    assert pausable_stream.signal is Signal.PAUSE

    # When data does come in, and it's late (or still catching up)
    # we can observe this in the latency info
    latency_info = await checkpoint.heartbeat(
        datetime(2025, 1, 1, 10, 30, tzinfo=UTC),
    )
    assert latency_info.get('is_late') is True

    # Latency info shows that the dependency stream has caught up
    latency_info = await checkpoint.heartbeat(
        datetime(2025, 1, 1, 11, 1, tzinfo=UTC),
    )
    assert latency_info.get('is_late') is False

    # Recovery observed, dependent resumed
    assert checkpoint['dependency'].is_down is False
    assert pausable_stream.signal is Signal.RESUME


@pytest.mark.parametrize('is_async', [True, False])
@pytest.mark.asyncio
async def test_custom_callbacks(is_async, checkpoint, mocker):
    """Check custom callbacks properly called."""
    if is_async:
        downtime_callback = mocker.AsyncMock()
        recovery_callback = mocker.AsyncMock()
    else:
        downtime_callback = mocker.Mock()
        recovery_callback = mocker.Mock()

    checkpoint._downtime_callback = downtime_callback
    checkpoint._recovery_callback = recovery_callback

    # Trigger downtime
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 10, tzinfo=UTC),
        state={'offset': 0},
    )
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 11, tzinfo=UTC),
        state={'offset': 1},
    )
    downtime_callback.assert_called_once_with(
        checkpoint,
        checkpoint['dependency'],
    )

    # Trigger recovery
    await checkpoint.heartbeat(
        datetime(2025, 1, 1, 11, 1, tzinfo=UTC),
    )
    recovery_callback.assert_called_once_with(
        checkpoint,
        checkpoint['dependency'],
    )


@pytest.mark.parametrize('is_async', [True, False])
@pytest.mark.asyncio
async def test_custom_checks(is_async, mock_cache, mocker):
    """Check custom check functions called."""
    if is_async:
        downtime_check = mocker.AsyncMock(return_value=timedelta(hours=1))
        recovery_check = mocker.AsyncMock(return_value=timedelta(hours=1))
    else:
        downtime_check = mocker.Mock(return_value=timedelta(hours=1))
        recovery_check = mocker.Mock(return_value=timedelta(hours=1))

    async def messages():
        yield {
            'event_timestamp': datetime(2025, 1, 1, 10, tzinfo=UTC),
        }

    dependency = Dependency(
        'dependency',
        messages(),
        downtime_check=downtime_check,
        recovery_check=recovery_check,
    )

    async def dependent():
        yield {
            'event_timestamp': datetime(2025, 1, 1, 10, tzinfo=UTC),
        }

    checkpoint = Checkpoint(
        'test', dependent(), [dependency], cache=mock_cache
    )

    # Trigger downtime
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 10, tzinfo=UTC),
        state={'offset': 0},
    )
    assert dependency.is_down is True
    await checkpoint.check_pulse(
        datetime(2025, 1, 1, 11, tzinfo=UTC),
        state={'offset': 1},
    )
    downtime_check.assert_called()

    # Trigger recovery
    await checkpoint.heartbeat(
        datetime(2025, 1, 1, 11, 1, tzinfo=UTC),
    )
    recovery_check.assert_called()
    assert dependency.is_down is False


def test_repr(checkpoint):
    """Should print representation without crashing."""
    assert str(checkpoint)
