from django.contrib import admin
from models import VaccinationBeneficiary, VaccineReminderTemplate, Vaccinations, VaccineReminder

class VaccineReminderAdmin(admin.ModelAdmin):
    readonly_fields = ('vaccine_reference', 'vaccination_beneficiary', 'state', 'errorCode')

admin.site.register(VaccinationBeneficiary)
admin.site.register(VaccineReminderTemplate)
admin.site.register(Vaccinations)
admin.site.register(VaccineReminder, VaccineReminderAdmin)