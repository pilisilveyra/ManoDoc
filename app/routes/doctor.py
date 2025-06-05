from datetime import date

from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify

from app.models.Doctor import Doctor
from app.models.Paciente import Paciente
from app.models.Turno import Turno

doctor_bp = Blueprint('doctor_bp', __name__, template_folder='templates')

@doctor_bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([
        {
            'id': doctor.id_doctor,
            'nombre': doctor.nombre,
            'apellido': doctor.apellido,
            'especialidad': doctor.especialidad,
            'imagen_url': doctor.foto
        }
        for doctor in doctors
    ])

