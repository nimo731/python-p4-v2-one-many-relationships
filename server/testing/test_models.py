import pytest
from datetime import datetime
from app import app
from models import db, Employee, Review, Onboarding

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def setup_database(app_context):
    # Clear existing data
    Employee.query.delete()
    Review.query.delete()
    Onboarding.query.delete()
    
    # Create test data
    employee1 = Employee(name="Test Employee 1", hire_date=datetime(2023, 1, 1))
    employee2 = Employee(name="Test Employee 2", hire_date=datetime(2023, 2, 1))
    
    db.session.add_all([employee1, employee2])
    db.session.commit()
    
    # Create reviews
    review1 = Review(year=2023, summary="Great work!", employee=employee1)
    review2 = Review(year=2023, summary="Good work!", employee=employee1)
    review3 = Review(year=2023, summary="Excellent work!", employee=employee2)
    
    db.session.add_all([review1, review2, review3])
    db.session.commit()
    
    # Create onboarding records
    onboarding1 = Onboarding(orientation=datetime(2023, 1, 2), forms_complete=True, employee=employee1)
    onboarding2 = Onboarding(orientation=datetime(2023, 2, 2), forms_complete=False, employee=employee2)
    
    db.session.add_all([onboarding1, onboarding2])
    db.session.commit()
    
    return {
        'employee1': employee1,
        'employee2': employee2,
        'review1': review1,
        'review2': review2,
        'review3': review3,
        'onboarding1': onboarding1,
        'onboarding2': onboarding2
    }

def test_employee_review_relationship(setup_database):
    """Test one-to-many relationship between Employee and Review"""
    employee1 = setup_database['employee1']
    employee2 = setup_database['employee2']
    
    # Test employee has multiple reviews
    assert len(employee1.reviews) == 2
    assert len(employee2.reviews) == 1
    
    # Test review belongs to correct employee
    review1 = setup_database['review1']
    assert review1.employee == employee1
    assert review1.employee_id == employee1.id

def test_employee_onboarding_relationship(setup_database):
    """Test one-to-one relationship between Employee and Onboarding"""
    employee1 = setup_database['employee1']
    employee2 = setup_database['employee2']
    
    # Test employee has one onboarding
    assert employee1.onboarding is not None
    assert employee2.onboarding is not None
    
    # Test onboarding belongs to correct employee
    onboarding1 = setup_database['onboarding1']
    assert onboarding1.employee == employee1
    assert onboarding1.employee_id == employee1.id

def test_cascade_delete(setup_database):
    """Test cascade delete functionality"""
    employee1 = setup_database['employee1']
    employee_id = employee1.id
    
    # Delete employee
    db.session.delete(employee1)
    db.session.commit()
    
    # Check that associated reviews and onboarding are deleted
    assert Review.query.filter_by(employee_id=employee_id).count() == 0
    assert Onboarding.query.filter_by(employee_id=employee_id).count() == 0

def test_review_creation(setup_database):
    """Test creating new reviews"""
    employee1 = setup_database['employee1']
    
    # Create new review
    new_review = Review(year=2024, summary="New review", employee=employee1)
    db.session.add(new_review)
    db.session.commit()
    
    # Verify review was added
    assert len(employee1.reviews) == 3
    assert new_review in employee1.reviews

def test_onboarding_creation(setup_database):
    """Test creating new onboarding record"""
    employee1 = setup_database['employee1']
    
    # Try to create new onboarding (should fail due to one-to-one relationship)
    new_onboarding = Onboarding(orientation=datetime(2024, 1, 1), employee=employee1)
    db.session.add(new_onboarding)
    
    # The commit should fail because employee1 already has an onboarding record
    with pytest.raises(Exception) as exc_info:
        db.session.commit()
    
    # Rollback the failed transaction
    db.session.rollback()
    
    # Verify that employee1 still has only one onboarding record
    assert len(Onboarding.query.filter_by(employee_id=employee1.id).all()) == 1

def test_employee_creation():
    """Test creating new employee"""
    with app.app_context():
        # Create new employee
        new_employee = Employee(name="New Employee", hire_date=datetime(2024, 1, 1))
        db.session.add(new_employee)
        db.session.commit()
        
        # Verify employee was created
        assert new_employee.id is not None
        assert Employee.query.filter_by(name="New Employee").first() is not None 