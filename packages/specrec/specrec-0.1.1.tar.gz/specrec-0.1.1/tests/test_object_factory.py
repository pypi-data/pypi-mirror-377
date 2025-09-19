"""Comprehensive test suite for ObjectFactory implementation."""

import threading
import time
from typing import List
from uuid import UUID

import pytest

from specrec import (
    ObjectFactory,
    clear_all,
    clear_one,
    context,
    create,
    create_direct,
    get_instance,
    get_registered_object,
    register_object,
    reset_instance,
    set_always,
    set_one,
)
from specrec.interfaces import ConstructorParameterInfo

from .test_examples.email_service import (
    EmailService,
    MultiConstructorService,
    NoArgsService,
    ServiceWithId,
    ServiceWithTracking,
    SqlRepository,
)
from .test_examples.mock_services import (
    FakeServiceWithTracking,
    MockEmailService,
    SpyService,
    StubRepository,
)


class TestBasicCreate:
    """Test basic object creation functionality (Microfeature 01)."""

    def test_create_curried_syntax(self):
        """Test curried syntax for object creation."""
        factory = ObjectFactory()
        create_service = factory.create(NoArgsService)

        service = create_service()

        assert isinstance(service, NoArgsService)
        assert service.created is True

    def test_create_global_function(self):
        """Test global create function."""
        reset_instance()  # Ensure clean state
        create_service = create(NoArgsService)

        service = create_service()

        assert isinstance(service, NoArgsService)
        assert service.created is True

    def test_create_direct_method(self):
        """Test direct creation method."""
        factory = ObjectFactory()

        service = factory.create_direct(NoArgsService)

        assert isinstance(service, NoArgsService)

    def test_create_direct_global_function(self):
        """Test global create_direct function."""
        reset_instance()
        service = create_direct(NoArgsService)

        assert isinstance(service, NoArgsService)

    def test_create_multiple_instances_are_different(self):
        """Test that multiple creations return different instances."""
        factory = ObjectFactory()
        create_service = factory.create(NoArgsService)

        service1 = create_service()
        service2 = create_service()

        assert service1 is not service2
        assert isinstance(service1, NoArgsService)
        assert isinstance(service2, NoArgsService)


class TestConstructorParameters:
    """Test constructor parameter support (Microfeature 02)."""

    def test_create_with_single_parameter(self):
        """Test creation with single constructor argument."""
        factory = ObjectFactory()
        create_service = factory.create(MultiConstructorService)

        service = create_service("test_name")

        assert service.mode == "name_only"
        assert service.name == "test_name"
        assert service.port == 80

    def test_create_with_multiple_parameters(self):
        """Test creation with multiple constructor arguments."""
        factory = ObjectFactory()
        create_repo = factory.create(SqlRepository)

        repo = create_repo("server=localhost;db=test", 60)

        assert repo.connection_string == "server=localhost;db=test"
        assert repo.timeout == 60

    def test_create_with_keyword_arguments(self):
        """Test creation with keyword arguments."""
        factory = ObjectFactory()
        create_service = factory.create(MultiConstructorService)

        service = create_service(config={"port": 8080}, name="config_service")

        assert service.mode == "config"
        assert service.name == "config_service"
        assert service.port == 8080

    def test_create_with_mixed_arguments(self):
        """Test creation with both positional and keyword arguments."""
        factory = ObjectFactory()
        create_email = factory.create(EmailService)

        service = create_email("smtp.gmail.com", port=587, username="test@example.com")

        assert service.smtp_server == "smtp.gmail.com"
        assert service.port == 587
        assert service.username == "test@example.com"

    def test_create_direct_with_parameters(self):
        """Test direct creation with parameters."""
        factory = ObjectFactory()

        service = factory.create_direct(SqlRepository, "connection_string", timeout=45)

        assert service.connection_string == "connection_string"
        assert service.timeout == 45


class TestInterfaceImplementation:
    """Test interface-like usage (Microfeature 03 - simplified for Python)."""

    def test_create_returns_correct_type(self):
        """Test that created objects have correct type."""
        factory = ObjectFactory()
        create_email = factory.create(EmailService)

        service = create_email("smtp.example.com")

        assert isinstance(service, EmailService)
        # Duck typing - works with any compatible interface
        assert hasattr(service, 'send')
        assert callable(service.send)

    def test_duck_typing_compatibility(self):
        """Test that duck typing works for interface compatibility."""
        factory = ObjectFactory()

        # Real service
        real_service = factory.create(EmailService)("smtp.real.com")
        # Mock service (no explicit interface implementation needed)
        mock_service = MockEmailService()

        # Both should be usable the same way
        assert real_service.send("test@example.com", "Test") is True
        assert mock_service.send("test@example.com", "Test") is True

        # Both have the same interface
        assert hasattr(real_service, 'send')
        assert hasattr(mock_service, 'send')


class TestTestDoubleInjectionSetOne:
    """Test single-use test double injection (Microfeature 04)."""

    def test_set_one_returns_test_double(self):
        """Test that set_one returns queued test double."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        factory.set_one(EmailService, mock_service)
        create_email = factory.create(EmailService)
        service = create_email("smtp.example.com")

        assert service is mock_service

    def test_set_one_consumed_on_use(self):
        """Test that test double is only returned once."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        factory.set_one(EmailService, mock_service)
        create_email = factory.create(EmailService)

        # First call returns mock
        service1 = create_email("smtp.example.com")
        assert service1 is mock_service

        # Second call creates new instance
        service2 = create_email("smtp.example.com")
        assert service2 is not mock_service
        assert isinstance(service2, EmailService)

    def test_set_one_falls_back_to_normal(self):
        """Test normal creation after test double consumed."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        factory.set_one(NoArgsService, mock_service)
        create_service = factory.create(NoArgsService)

        # Get the mock
        service1 = create_service()
        assert service1 is mock_service

        # Get normal instance
        service2 = create_service()
        assert isinstance(service2, NoArgsService)
        assert service2 is not mock_service

    def test_set_one_multiple_queued_fifo(self):
        """Test multiple test doubles queued in FIFO order."""
        factory = ObjectFactory()
        mock1 = MockEmailService()
        mock2 = MockEmailService()
        mock1.test_id = "mock1"
        mock2.test_id = "mock2"

        factory.set_one(EmailService, mock1)
        factory.set_one(EmailService, mock2)
        create_email = factory.create(EmailService)

        service1 = create_email("smtp.example.com")
        service2 = create_email("smtp.example.com")

        assert service1 is mock1
        assert service2 is mock2

    def test_set_one_global_function(self):
        """Test set_one using global function."""
        reset_instance()
        mock_service = MockEmailService()

        set_one(EmailService, mock_service)
        create_email = create(EmailService)
        service = create_email("smtp.example.com")

        assert service is mock_service


class TestTestDoubleInjectionSetAlways:
    """Test persistent test double injection (Microfeature 05)."""

    def test_set_always_returns_test_double(self):
        """Test that set_always returns test double."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        factory.set_always(EmailService, mock_service)
        create_email = factory.create(EmailService)

        service1 = create_email("smtp.example.com")
        service2 = create_email("smtp.example.com")

        assert service1 is mock_service
        assert service2 is mock_service

    def test_set_always_overrides_set_one(self):
        """Test that set_always takes precedence over set_one."""
        factory = ObjectFactory()
        mock_one = MockEmailService()
        mock_always = MockEmailService()
        mock_one.test_id = "one"
        mock_always.test_id = "always"

        factory.set_one(EmailService, mock_one)
        factory.set_always(EmailService, mock_always)

        create_email = factory.create(EmailService)
        service = create_email("smtp.example.com")

        assert service is mock_always
        # set_one queue should still have the mock
        # Clear only the always mapping to test the set_one fallback
        factory._set_always.pop(EmailService, None)
        service2 = create_email("smtp.example.com")
        assert service2 is mock_one

    def test_set_always_global_function(self):
        """Test set_always using global function."""
        reset_instance()
        mock_service = MockEmailService()

        set_always(EmailService, mock_service)
        create_email = create(EmailService)

        service1 = create_email("smtp.example.com")
        service2 = create_email("smtp.example.com")

        assert service1 is mock_service
        assert service2 is mock_service


class TestClearOperations:
    """Test cleanup methods for test isolation (Microfeature 06)."""

    def test_clear_one_removes_test_doubles(self):
        """Test that clear_one removes test doubles for specific type."""
        factory = ObjectFactory()
        mock_email = MockEmailService()
        mock_repo = StubRepository()

        factory.set_one(EmailService, mock_email)
        factory.set_always(SqlRepository, mock_repo)

        factory.clear_one(EmailService)

        # EmailService should create normally
        create_email = factory.create(EmailService)
        email = create_email("smtp.example.com")
        assert isinstance(email, EmailService)

        # SqlRepository should still return mock
        create_repo = factory.create(SqlRepository)
        repo = create_repo("connection")
        assert repo is mock_repo

    def test_clear_all_removes_all_test_doubles(self):
        """Test that clear_all removes all test doubles."""
        factory = ObjectFactory()
        mock_email = MockEmailService()
        mock_repo = StubRepository()

        factory.set_one(EmailService, mock_email)
        factory.set_always(SqlRepository, mock_repo)

        factory.clear_all()

        # Both should create normally
        email = factory.create(EmailService)("smtp.example.com")
        repo = factory.create(SqlRepository)("connection")

        assert isinstance(email, EmailService)
        assert isinstance(repo, SqlRepository)

    def test_clear_global_functions(self):
        """Test clear functions using global API."""
        reset_instance()
        mock_email = MockEmailService()
        mock_repo = StubRepository()

        set_one(EmailService, mock_email)
        set_always(SqlRepository, mock_repo)

        clear_one(EmailService)
        email = create(EmailService)("smtp.example.com")
        repo = create(SqlRepository)("connection")

        assert isinstance(email, EmailService)
        assert repo is mock_repo

        clear_all()
        repo2 = create(SqlRepository)("connection")
        assert isinstance(repo2, SqlRepository)


class TestGlobalInstance:
    """Test global/static factory access (Microfeature 07)."""

    def test_global_instance_singleton(self):
        """Test that get_instance returns same instance."""
        reset_instance()

        instance1 = get_instance()
        instance2 = get_instance()

        assert instance1 is instance2

    def test_global_instance_thread_safe(self):
        """Test thread-safe global instance initialization."""
        reset_instance()
        instances = []

        def get_instance_thread():
            instances.append(get_instance())

        threads = [threading.Thread(target=get_instance_thread) for _ in range(10)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All threads should get the same instance
        assert len(set(id(instance) for instance in instances)) == 1

    def test_global_functions_use_singleton(self):
        """Test that global functions use the same singleton."""
        reset_instance()
        mock_service = MockEmailService()

        # Use global function
        set_one(EmailService, mock_service)

        # Use instance directly
        instance = get_instance()
        create_email = instance.create(EmailService)
        service = create_email("smtp.example.com")

        # Should return the same mock
        assert service is mock_service

    def test_reset_instance_clears_singleton(self):
        """Test that reset_instance creates new singleton."""
        instance1 = get_instance()
        reset_instance()
        instance2 = get_instance()

        assert instance1 is not instance2


class TestConstructorParameterTracking:
    """Test constructor parameter tracking (Microfeature 08)."""

    def test_constructor_parameter_tracking(self):
        """Test that constructor parameters are tracked."""
        factory = ObjectFactory()
        create_service = factory.create(ServiceWithTracking)

        service = create_service("test_service", 8080, enabled=False)

        assert len(service.constructor_params) == 3

        # Check positional parameters
        assert service.constructor_params[0]["index"] == 0
        assert service.constructor_params[0]["name"] == "name"
        assert service.constructor_params[0]["value"] == "test_service"
        assert service.constructor_params[0]["type_name"] == "str"

        assert service.constructor_params[1]["index"] == 1
        assert service.constructor_params[1]["name"] == "port"
        assert service.constructor_params[1]["value"] == 8080
        assert service.constructor_params[1]["type_name"] == "int"

        # Check keyword parameter
        assert service.constructor_params[2]["index"] == 2
        assert service.constructor_params[2]["name"] == "enabled"
        assert service.constructor_params[2]["value"] is False
        assert service.constructor_params[2]["type_name"] == "bool"

    def test_parameter_tracking_with_test_double(self):
        """Test that parameter tracking works with test doubles."""
        factory = ObjectFactory()
        fake_service = FakeServiceWithTracking()

        factory.set_one(ServiceWithTracking, fake_service)
        create_service = factory.create(ServiceWithTracking)

        service = create_service("name", 123)

        # Should return the fake service without tracking parameters
        assert service is fake_service
        assert len(service.constructor_params) == 0  # No tracking for test doubles

    def test_parameter_tracking_no_interface_no_error(self):
        """Test that objects without IConstructorCalledWith don't cause errors."""
        factory = ObjectFactory()
        create_service = factory.create(NoArgsService)

        # Should not raise an exception
        service = create_service()
        assert isinstance(service, NoArgsService)


class TestObjectRegistration:
    """Test object registration for clean logging (Microfeature 09)."""

    def test_register_object_with_generated_id(self):
        """Test registering object with auto-generated ID."""
        factory = ObjectFactory()
        service = ServiceWithId("test_service")

        object_id = factory.register_object(service)

        # Should generate valid UUID
        UUID(object_id)  # Will raise ValueError if not valid UUID

        # Should be retrievable
        retrieved = factory.get_registered_object(object_id)
        assert retrieved is service

    def test_register_object_with_custom_id(self):
        """Test registering object with custom ID."""
        factory = ObjectFactory()
        service = ServiceWithId("test_service")
        custom_id = "custom_service_123"

        object_id = factory.register_object(service, custom_id)

        assert object_id == custom_id
        retrieved = factory.get_registered_object(object_id)
        assert retrieved is service

    def test_register_object_sets_id_property(self):
        """Test that registration sets object_id property if supported."""
        factory = ObjectFactory()
        service = ServiceWithId("test_service")

        object_id = factory.register_object(service)

        assert service.object_id == object_id

    def test_register_object_global_functions(self):
        """Test object registration using global functions."""
        reset_instance()
        service = ServiceWithId("test_service")

        object_id = register_object(service, "global_test")

        retrieved = get_registered_object("global_test")
        assert retrieved is service
        assert object_id == "global_test"

    def test_clear_all_clears_registered_objects(self):
        """Test that clear_all removes registered objects."""
        factory = ObjectFactory()
        service = ServiceWithId("test_service")

        object_id = factory.register_object(service)
        factory.clear_all()

        retrieved = factory.get_registered_object(object_id)
        assert retrieved is None


class TestContextManager:
    """Test context manager for test isolation."""

    def test_context_manager_isolates_test_doubles(self):
        """Test that context manager provides isolation."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        with factory.context():
            factory.set_one(EmailService, mock_service)
            service = factory.create(EmailService)("smtp.example.com")
            assert service is mock_service

        # Outside context, should create normally
        service2 = factory.create(EmailService)("smtp.example.com")
        assert isinstance(service2, EmailService)
        assert service2 is not mock_service

    def test_context_manager_global_function(self):
        """Test context manager using global function."""
        reset_instance()
        mock_service = MockEmailService()

        with context():
            set_one(EmailService, mock_service)
            service = create(EmailService)("smtp.example.com")
            assert service is mock_service

        # Outside context, should create normally
        service2 = create(EmailService)("smtp.example.com")
        assert isinstance(service2, EmailService)

    def test_context_manager_nested(self):
        """Test nested context managers."""
        factory = ObjectFactory()
        mock1 = MockEmailService()
        mock2 = MockEmailService()
        mock1.test_id = "outer"
        mock2.test_id = "inner"

        with factory.context():
            factory.set_always(EmailService, mock1)

            with factory.context():
                factory.set_always(EmailService, mock2)
                service = factory.create(EmailService)("smtp.example.com")
                assert service is mock2

            # Back to outer context
            service = factory.create(EmailService)("smtp.example.com")
            assert service is mock1

        # Outside all contexts
        service = factory.create(EmailService)("smtp.example.com")
        assert isinstance(service, EmailService)

    def test_context_manager_exception_handling(self):
        """Test that context manager cleans up even on exceptions."""
        factory = ObjectFactory()
        mock_service = MockEmailService()

        try:
            with factory.context():
                factory.set_always(EmailService, mock_service)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should still be cleaned up
        service = factory.create(EmailService)("smtp.example.com")
        assert isinstance(service, EmailService)
        assert service is not mock_service


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_create_with_none_class(self):
        """Test creating with None class raises appropriate error."""
        factory = ObjectFactory()

        with pytest.raises(TypeError):
            factory.create(None)

    def test_create_with_invalid_arguments(self):
        """Test creation with invalid constructor arguments."""
        factory = ObjectFactory()
        create_service = factory.create(SqlRepository)

        # Should raise TypeError for missing required arguments
        with pytest.raises(TypeError):
            create_service()  # Missing required connection_string

    def test_clear_one_nonexistent_type(self):
        """Test clearing nonexistent type doesn't cause errors."""
        factory = ObjectFactory()

        # Should not raise exception
        factory.clear_one(EmailService)

    def test_get_registered_object_nonexistent_id(self):
        """Test getting nonexistent registered object returns None."""
        factory = ObjectFactory()

        result = factory.get_registered_object("nonexistent_id")
        assert result is None

    def test_thread_safety_concurrent_creation(self):
        """Test concurrent object creation is thread-safe."""
        factory = ObjectFactory()
        results = []
        exceptions = []

        def create_service():
            try:
                service = factory.create(NoArgsService)()
                results.append(service)
            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=create_service) for _ in range(20)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(exceptions) == 0
        assert len(results) == 20
        assert all(isinstance(result, NoArgsService) for result in results)

    def test_thread_safety_concurrent_test_double_injection(self):
        """Test concurrent test double injection is thread-safe."""
        factory = ObjectFactory()
        mock_services = []
        results = []

        def inject_and_create(mock_id):
            mock = MockEmailService()
            mock.test_id = mock_id
            mock_services.append(mock)

            factory.set_one(EmailService, mock)
            service = factory.create(EmailService)("smtp.example.com")
            results.append(service)

        threads = [threading.Thread(target=inject_and_create, args=(i,)) for i in range(10)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(results) == 10
        # All should be mock services (due to injection)
        assert all(isinstance(result, MockEmailService) for result in results)