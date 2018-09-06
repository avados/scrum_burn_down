from django.utils import timezone
from datetime import datetime, timedelta, date
from django.core.validators import ValidationError

def validate_snapshot_date(_date):
	if _date == None:
		return datetime.now()
	elif _date >= (timezone.now() + timedelta(days=1)).date():
		raise ValidationError('Pbi cannot be in the future')
	
	return _date
	
def validate_sprint():
	print( "prout" )
	
	