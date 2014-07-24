from django.contrib import admin
from models import VaccinationBeneficiary, VaccineReminderTemplate, Vaccinations, VaccineStatus

class VaccineStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('VaccineReminder', 'vaccination_beneficiary', 'state', 'errorCode')

admin.site.register(VaccinationBeneficiary)
admin.site.register(VaccineReminderTemplate)
admin.site.register(Vaccinations)
admin.site.register(VaccineStatus, VaccineStatusAdmin)