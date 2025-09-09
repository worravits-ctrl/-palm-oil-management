from forms import FertilizerForm

form = FertilizerForm()
form.spreading_wage.data = 0
print("Can accept 0:", form.spreading_wage.validate())
