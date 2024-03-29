from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, \
    DepartmentSchedule, PrescriptionMedicine
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar', 'role', 'last_login']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # def get_avatar(self, user):
    #     if user.avatar:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(user.avatar)
    #         return user.avatar.url
    #     return None

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        return u


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'avatar', 'phone_nb']

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class BaseSerialize(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='avatar')

    def get_image(self, patient):
        if patient.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('https://res.cloudinary.com/drbd9x4ha/%s' % patient.avatar)

            return 'https://res.cloudinary.com/drbd9x4ha/%s' % patient.avatar


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        select_related = ['user_info']


class DoctorSerializer(serializers.ModelSerializer):
    user_info = UserSerializer()

    class Meta:
        model = Doctor
        fields = '__all__'
        select_related = ['user_info']


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = '__all__'
        select_related = ['user_info']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class MedicineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'weight']


class MedicineNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['name']


class MedicineDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class ReceiptPaidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = ['total', 'paid']


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'symptoms', 'diagnosis', 'patient', 'doctor', 'medicines', 'services']
        select_related = ['patient', 'doctor']
        prefetch_related = ['medicines', 'services']


class PrescriptionListSerializer(serializers.ModelSerializer):
    receipt = ReceiptPaidSerializer()
    doctor = UserNameSerializer(source='doctor.user_info')

    class Meta:
        model = Prescription
        fields = ['id', 'diagnosis', 'doctor', 'created_date', 'receipt']


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    medicine = MedicineNameSerializer()
    class Meta:
        model = PrescriptionMedicine
        fields = ['id', 'prescription', 'medicine', 'quantity', 'dosage']


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    dosages = PrescriptionMedicineSerializer(many=True)
    receipt = ReceiptPaidSerializer()

    class Meta:
        model = Prescription
        fields = ['id', 'symptoms', 'diagnosis', 'patient', 'doctor', 'services', 'dosages', 'receipt']
        select_related = ['patient', 'doctor']
        prefetch_related = ['medicines', 'services']


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
        select_related = ['nurse', 'prescription']


class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserNameSerializer(source="patient.user_info")

    class Meta:
        model = Appointment
        fields = '__all__'
