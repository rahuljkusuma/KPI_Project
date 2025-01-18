from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
from .models import Company
import requests
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import io


def fetch_nse_data():
  """
  Fetches equity data from NSE and stores in database table.
  """
  nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
  headers = {'User-Agent':'Mozilla/5.0'}

  try:
    with requests.Session() as session:
      session.headers.update(headers)
      response = session.get(nse_url)
      response.raise_for_status()

      df_nse = pd.read_csv(io.BytesIO(response.content))

    if "SYMBOL" not in df_nse.columns or "NAME OF COMPANY" not in df_nse.columns:
      return JsonResponse({"success": False, "error": "Missing required columns in CSV file."})

    # Assuming you have a model named 'Company' with 'name' and 'symbol' fields
    # Modify this part to fit your actual model
    companies = []
    for index, row in df_nse.iterrows():
      companies.append(Company(name=row['NAME OF COMPANY'], symbol=row['SYMBOL']))
    Company.objects.bulk_create(companies)

    return JsonResponse({"success": True, "message": "Data fetched and stored successfully."})

  except requests.exceptions.RequestException as e:
    return JsonResponse({"success": False, "error": str(e)})
  except Exception as e:
    return JsonResponse({"success": False, "error": "An error occurred while processing the data: " + str(e)})

@csrf_exempt
def search_companies(request):
  if request.method == "POST":
    query = request.POST.get('q')
    if query:
      # Implement search logic here to fetch companies from database
      companies = Company.objects.filter(name__icontains=query)[:10]  # Limit to 10 suggestions
      suggestions = [company.name for company in companies]
      return JsonResponse(suggestions, safe=False)  # Avoid HTML escaping for list
  return JsonResponse([])