from assertpy.assertpy import assert_that
from pydm import ServiceContainer, InMemoryParametersBag
from pydm.parameters_bag import ParametersBagInterface


class DummyUnitOfWork:
    pass
class RepositoryStub:
    def __init__(self, unit_of_work: DummyUnitOfWork):
        self.unit_of_work = unit_of_work
class UseCaseStub:
    def __init__(self, repository: RepositoryStub):
        self.repository = repository

class DummyInterface:
    pass
class DummyImplementation(DummyInterface):
    pass

class DummyClass:
    def __init__(self, stub_val: str):
        self.stub_val = stub_val
class DummyClassFactoryStub:
    def make(self):
        return DummyClass('CFF')

class ClassSub:
    def __init__(self, value: str):
        self.value = value

def test_only_one_instance_of_service_container_exists() -> None:
    # arrange
    sut: ServiceContainer = ServiceContainer.get_instance()

    # act
    instance2: ServiceContainer = ServiceContainer.get_instance()
    instance3: ServiceContainer = ServiceContainer()

    # assert
    assert_that(instance2).is_equal_to(sut)
    assert_that(instance3).is_equal_to(sut)

def test_service_container_resolves_service_dependencies_automatically() -> None:
    # arrange
    sut: ServiceContainer = ServiceContainer.get_instance()

    # act
    desired_service = sut.get_service(UseCaseStub)

    # assert
    assert_that(desired_service).is_instance_of(UseCaseStub)
    assert_that(desired_service.repository).is_instance_of(RepositoryStub)
    assert_that(desired_service.repository.unit_of_work).is_instance_of(DummyUnitOfWork)

def test_service_container_use_bounded_implementation_for_an_interface() -> None:
    # arrange
    sut: ServiceContainer = ServiceContainer.get_instance()
    sut.bind(DummyInterface, DummyImplementation)

    # act
    impl = sut.get_service(DummyInterface)

    # assert
    assert_that(impl).is_instance_of(DummyImplementation)

def test_service_container_use_bounded_factory_to_make_the_service() -> None:
    # arrange
    sut: ServiceContainer = ServiceContainer.get_instance()
    sut.bind_to_factory(DummyClass, DummyClassFactoryStub, 'make')

    # act
    maked_service = sut.get_service(DummyClass)

    # assert
    assert_that(maked_service).is_instance_of(DummyClass)
    assert_that(maked_service.stub_val).is_equal_to('CFF')

def test_service_container_use_parameters_when_service_a_dependency_is_value() -> None:
    # arrange
    sut: ServiceContainer = ServiceContainer.get_instance()
    parameters: ParametersBagInterface = InMemoryParametersBag({
        'DUMMY_VALUE': 'vfp'
    })
    sut.set_parameters(parameters)
    sut.bind_parameters(ClassSub, {'value': 'DUMMY_VALUE'})

    # act
    cls = sut.get_service(ClassSub)

    # assert
    assert_that(cls.value).is_equal_to('vfp')