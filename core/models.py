from django.db import models
from django.contrib.auth.models import User

# 1. PACIENTE (DNI único)
class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=[('M', 'M'), ('F', 'F'), ('O', 'O')], blank=True)
    notas = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dni})"

    # 2. CUIDADOR
class Cuidador(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username

# 3. DISPOSITIVO
class Dispositivo(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, unique=True, default="LENTES-001")
    nombre = models.CharField(max_length=100, default="Lentes Sensoriales")
    estado = models.CharField(max_length=20, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='INACTIVO')
    ultima_conexion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

# 4. SESIÓN (clave: activa=True)
class SesionPaciente(models.Model):
    id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.SET_NULL, null=True)
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.paciente} - {'Activa' if self.activa else 'Finalizada'}"

# 5. DATO SENSOR
class DatoSensor(models.Model):
    id = models.AutoField(primary_key=True)
    sesion = models.ForeignKey(SesionPaciente, on_delete=models.CASCADE)
    color = models.CharField(max_length=20)
    temperatura = models.FloatField()
    distancia = models.FloatField()
    nivel = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

# 6. ALERTA
class Alerta(models.Model):
    id = models.AutoField(primary_key=True)
    sesion = models.ForeignKey(SesionPaciente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20)
    mensaje = models.CharField(max_length=100)
    severidad = models.CharField(max_length=10, default='MEDIA')
    vista = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

# 7. COMANDO
class ComandoControl(models.Model):
    id = models.AutoField(primary_key=True)
    sesion = models.ForeignKey(SesionPaciente, on_delete=models.CASCADE)
    comando = models.CharField(max_length=50)
    parametros = models.CharField(max_length=100, blank=True)
    ejecutado = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

# 8. MENSAJE OLED
class MensajeCuidador(models.Model):
    id = models.AutoField(primary_key=True)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    sesion = models.ForeignKey(SesionPaciente, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=128)
    leido = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)