import streamlit as st
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            port=3306,
            password='',
            database='Database for Hospital Management Application'
        )
        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def register_user(connection, name, birthdate, phone, email, city, state, zip_code):
    cursor = connection.cursor()
    user_query = """
        INSERT INTO User (Name, BirthDate, Phone, EMail, City, State, ZIP)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    user_values = (name, birthdate.strftime('%Y-%m-%d'), phone, email, city, state, zip_code)
    cursor.execute(user_query, user_values)
    connection.commit()
    user_id = cursor.lastrowid  # Get the ID of the newly created user
    cursor.close()
    return user_id

def register_employee(connection, user_id, hired_date, employee_type, additional_fields):
    cursor = connection.cursor()
    employee_query = """
        INSERT INTO Employee (EUniqueIdentifier, HiredDate) VALUES (%s, %s)
    """
    cursor.execute(employee_query, (user_id, hired_date.strftime('%Y-%m-%d')))
    
    if employee_type == "Nurse":
        nurse_query = """
            INSERT INTO Nurse (EUniqueIdentifier, PhUniqueIdentifier, CertificateOrDegree, AuxiliaryOrProfessional)
            VALUES (%s, %s, %s, %s)
        """
        nurse_values = (user_id, additional_fields['ph_unique_identifier'], additional_fields['certificate_degree'], additional_fields['auxiliary_professional'])
        cursor.execute(nurse_query, nurse_values)
    elif employee_type == "Staff":
        staff_query = """
            INSERT INTO Staff (EUniqueIdentifier, PaUniqueIdentifier) VALUES (%s, %s)
        """
        staff_values = (user_id, additional_fields['pa_unique_identifier'])
        cursor.execute(staff_query, staff_values)
    
    connection.commit()
    cursor.close()

def register_physician(connection, user_id, pagerNumber):
    cursor = connection.cursor()
    physician_query = """
        INSERT INTO Physician (PhUniqueIdentifier, PagerNumber) VALUES (%s, %s)
    """
    cursor.execute(physician_query, (user_id, pagerNumber))
    connection.commit()
    cursor.close()

def register_patient(connection, user_id, contract_date, has_insurance, emergency_contact, insurance_info, referral_info):
    cursor = connection.cursor()
    patient_query = """
        INSERT INTO Patient (PaUniqueIdentifier, ContractDate, HasInsurance) VALUES (%s, %s, %s)
    """
    cursor.execute(patient_query, (user_id, contract_date.strftime('%Y-%m-%d'), has_insurance))
    connection.commit()

    emergency_query = """
        INSERT INTO EmergencyContact (PaUniqueIdentifier, ContactLastName, ContactFirstName, ContractRelationship, ContactAddress, ContactPhone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(emergency_query, (user_id, emergency_contact['last_name'], emergency_contact['first_name'],
                                     emergency_contact['relationship'], emergency_contact['address'], emergency_contact['phone']))
    
    if has_insurance:
        insurance_query = """
            INSERT INTO PatientWithInsurance (PaUniqueNumber, PolicyNumber, InsuranceCompanyID, GroupNumber)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insurance_query, (user_id, insurance_info['policy_number'], insurance_info['insurance_company_id'], insurance_info['group_number']))
    else:
        insurance_query = """
            INSERT INTO PatientWithoutInsurance (PaUniqueNumber, SubscriberLastName, SubscriberFirstName, SubscriberRelationship, SubscriberAddress, SubscriberPhone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insurance_query, (user_id, insurance_info['subscriber_last_name'],
                                         insurance_info['subscriber_first_name'], insurance_info['subscriber_relationship'],
                                         insurance_info['subscriber_address'], insurance_info['subscriber_phone']))

    referral_query = """
        INSERT INTO ReferralPhysician (PaUniqueIdentifier, ReferralLastName, ReferralFirstName, ReferralAddress, ReferralPhone)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(referral_query, (user_id, referral_info['last_name'], referral_info['first_name'], referral_info['address'], referral_info['phone']))
    
    connection.commit()
    cursor.close()

def main():
    st.title("User Registration for Hospital Management Application")

    name = st.text_input("Name")
    birthdate = st.date_input("Birth Date")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    city = st.text_input("City")
    state = st.text_input("State")
    zip_code = st.text_input("ZIP Code")

    user_type = st.selectbox("User Type", ["Employee", "Physician", "Patient"])

    if user_type == "Employee":
        hired_date = st.date_input("Date Hired")
        employee_type = st.selectbox("Employee Type", ["Nurse", "Staff"])
        additional_fields = {}
        if employee_type == "Nurse":
            additional_fields['ph_unique_identifier'] = st.number_input("Physician to Assist (PhUniqueIdentifier)", min_value=1)
            additional_fields['certificate_degree'] = st.text_input("Certificate or Degree")
            additional_fields['auxiliary_professional'] = st.selectbox("Auxiliary or Professional", ["Auxiliary", "Professional"])
        elif employee_type == "Staff":
            additional_fields['pa_unique_identifier'] = st.number_input("Patient to Assist (PaUniqueIdentifier)", min_value=1)
    elif user_type == "Physician":
        pagerNumber = st.text_input("Pager Number")
    elif user_type == "Patient":
        contract_date = st.date_input("Contract Date")
        has_insurance = st.checkbox("Has Insurance")
        emergency_contact = {
            'last_name': st.text_input("Emergency Contact Last Name"),
            'first_name': st.text_input("Emergency Contact First Name"),
            'relationship': st.text_input("Relationship to Patient"),
            'address': st.text_input("Emergency Contact Address"),
            'phone': st.text_input("Emergency Contact Phone")
        }
        insurance_info = {}
        if has_insurance:
            insurance_info['policy_number'] = st.text_input("Policy Number")
            insurance_info['insurance_company_id'] = st.number_input("Insurance Company ID", min_value=1)
            insurance_info['group_number'] = st.text_input("Group Number")
        else:
            insurance_info['subscriber_last_name'] = st.text_input("Subscriber Last Name")
            insurance_info['subscriber_first_name'] = st.text_input("Subscriber First Name")
            insurance_info['subscriber_relationship'] = st.text_input("Subscriber Relationship")
            insurance_info['subscriber_address'] = st.text_input("Subscriber Address")
            insurance_info['subscriber_phone'] = st.text_input("Subscriber Phone")
        referral_info = {
            'last_name': st.text_input("Referral Physician Last Name"),
            'first_name': st.text_input("Referral Physician First Name"),
            'address': st.text_input("Referral Physician Address"),
            'phone': st.text_input("Referral Physician Phone")
        }

    if st.button("Register"):
        connection = create_connection()
        if connection:
            user_id = register_user(connection, name, birthdate, phone, email, city, state, zip_code)
            if user_type == "Employee":
                register_employee(connection, user_id, hired_date, employee_type, additional_fields)
                st.success("Employee registered successfully!")
            elif user_type == "Physician":
                register_physician(connection, user_id, pagerNumber)
                st.success("Physician registered successfully!")
            elif user_type == "Patient":
                register_patient(connection, user_id, contract_date, has_insurance, emergency_contact, insurance_info, referral_info)
                st.success("Patient registered successfully!")
            connection.close()

if __name__ == "__main__":
    main()
