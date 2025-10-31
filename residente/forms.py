from django import forms
from usuario.models import *
from django.core.validators import MaxValueValidator, MinValueValidator


class DetalleResidenteForm(forms.ModelForm):

    class Meta:
        model = DetalleResidente
        fields = ['propietario', 'torre', 'apartamento']
        widgets = {
            'propietario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generar torres (1 a 5)
        torres = [(i, f"Torre {i}") for i in range(1, 6)]

        # Generar apartamentos: 101–109, 201–209, ... hasta 1601–1609
        apartamentos = []
        for piso in range(1, 17):
            for num in range(1, 10):
                apto = piso * 100 + num
                apartamentos.append((apto, f"Apartamento {apto}"))

        # Reemplazar los widgets por selects con nuestras opciones
        self.fields['torre'] = forms.ChoiceField(
            choices=torres,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label="Torre"
        )
        self.fields['apartamento'] = forms.ChoiceField(
            choices=apartamentos,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label="Apartamento"
        )

    def clean(self):
        cleaned_data = super().clean()
        torre = cleaned_data.get("torre")
        apartamento = cleaned_data.get("apartamento")

        if torre and apartamento:
            existe = DetalleResidente.objects.filter(
                torre=torre,
                apartamento=apartamento
            ).exists()
            if existe:
                raise ValidationError(
                    f"El apartamento {apartamento} en la Torre {torre} ya está registrado."
                )
        return cleaned_data

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['hora_inicio', 'hora_fin', 'fecha_uso']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'fecha_uso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            # ❌ No puede ser la misma hora
            if hora_inicio == hora_fin:
                raise forms.ValidationError("La hora de finalización no puede ser igual a la hora de inicio.")

            # ❌ No puede ser antes de la hora de inicio
            if hora_fin < hora_inicio:
                raise forms.ValidationError("La hora de finalización no puede ser anterior a la hora de inicio.")

        return cleaned_data

class VehiculoResidenteForm(forms.ModelForm):
    class Meta:
        model = VehiculoResidente
        fields = ['placa', 'tipo_vehiculo']
        widgets = {
            'placa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ASD-123 o ASD-45D'
            }),
            'tipo_vehiculo': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').upper().strip()

        # Remover guiones y espacios
        placa = placa.replace('-', '').replace(' ', '')

        # Validar longitud básica
        if len(placa) not in [5, 6]:
            raise forms.ValidationError("La placa debe tener 5 o 6 caracteres (sin guión).")

        # Validar solo letras y números
        if not re.match(r'^[A-Z0-9]+$', placa):
            raise forms.ValidationError("La placa solo puede contener letras y números.")

        # ✅ Verificar si la placa ya existe (sin importar mayúsculas/minúsculas)
        model = self._meta.model  # Usa el modelo ya asociado al form
        placa_formateada = f"{placa[:3]}-{placa[3:]}" if len(placa) in [5, 6] else placa

        existente = model.objects.filter(placa__iexact=placa_formateada).first()
        if existente and (not self.instance or existente.pk != self.instance.pk):
            raise forms.ValidationError("La placa ya está registrada por otro usuario.")

        return placa

    def clean(self):
        cleaned_data = super().clean()
        placa = cleaned_data.get('placa')
        tipo_vehiculo = cleaned_data.get('tipo_vehiculo')

        if not placa or not tipo_vehiculo:
            return cleaned_data

        placa_formateada = None

        # 🚗 Carro
        if tipo_vehiculo == 'Carro':
            if len(placa) != 6:
                raise forms.ValidationError({
                    'placa': "Los carros deben tener 6 caracteres (formato: AAA123)"
                })
            if not (placa[:3].isalpha() and placa[3:].isdigit()):
                raise forms.ValidationError({
                    'placa': "Formato inválido para carro. Debe ser: AAA123 (3 letras y 3 números)"
                })
            placa_formateada = f"{placa[:3]}-{placa[3:]}"

        # 🏍️ Moto
        elif tipo_vehiculo == 'Moto':
            if len(placa) != 6:
                raise forms.ValidationError({
                    'placa': "Las motos deben tener 6 caracteres (formato: ASD45D)"
                })
            if not (placa[:3].isalpha() and placa[3:5].isdigit() and placa[-1].isalpha()):
                raise forms.ValidationError({
                    'placa': "Formato inválido para moto. Debe ser: ASD45D (3 letras, 2 números y 1 letra)"
                })
            placa_formateada = f"{placa[:3]}-{placa[3:]}"

        cleaned_data['placa'] = placa_formateada
        return cleaned_data


class ArchivoVehiculoForm(forms.ModelForm):
    class Meta:
        model = ArchivoVehiculo
        fields = ['idTipoArchivo', 'fechaVencimiento', 'archivo']
        labels = {
            'idTipoArchivo': 'Tipo de archivo',
            'fechaVencimiento': 'Fecha de vencimiento',
            'archivo': 'Archivo',
        }
        widgets = {
            'idTipoArchivo': forms.Select(attrs={'id': 'idTipoArchivo', 'class': 'form-select'}),
            'fechaVencimiento': forms.DateInput(attrs={'id': 'idFechaVencimiento', 'class': 'form-control', 'type': 'date'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['idTipoArchivo'].required = True
        self.fields['fechaVencimiento'].required = True
        self.fields['archivo'].required = True

class PagosReservaForm(forms.ModelForm):
    class Meta:
        model = PagosReserva
        fields = ["id_reserva", "archivo_1", "archivo_2", "estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Ocultar id_reserva y estado (el usuario no los ve)
        self.fields["id_reserva"].widget = forms.HiddenInput()
        self.fields["estado"].widget = forms.HiddenInput()

        # 🔹 Quitar el "Currently / Clear / Change" y usar solo input de archivo limpio
        self.fields["archivo_1"].widget = forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png",
            }
        )
        self.fields["archivo_2"].widget = forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png",
            }
        )