from django.shortcuts import render
from .forms import UploadFileForm, SearchFileForm
from .utils import *
from .models import *


def home(request):
    return render(request, 'statements/home.html')


def search(request):
    items = []
    row = None
    file_name = None
    message = ""
    if request.method == "POST":
        form = SearchFileForm(request.POST, request.FILES)
        file = request.FILES.getlist("file")[0]
        if isFilePDF(file):
            title = generate_package_date(file)
            items = extract_pdf(file)
            file_name = str(file)
            rows = LoanData.objects.filter(package_date=title)
            if rows.count() > 0:
                row = construct_meta(rows)
            else:
                row = None
        else:
            message = True
    else:
        file = ""
        form = SearchFileForm()

    return render(request, 'statements/search.html', {'form': form, "message": message, "items": items, "row": row,
                                                       "file_name": file_name})


def upload(request):
    message = ""
    error = False
    if request.method == "POST":
        print("POST")
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES.getlist("file")[0]
        if isFileCsv(file):
            if isLoanLevelDataExists(file):
                message = "Loan Level Data already exist."
                error = True
            else:
                llds = read_csv_file(file)
                llds_obj = LoanData.objects.bulk_create(llds)
                message = "Files has been saved."
        else:
            error = True
            message = "Please upload a csv file"
    else:
        form = UploadFileForm()

    return render(request, 'statements/upload.html', {"form": form, "message": message, "error": error})
