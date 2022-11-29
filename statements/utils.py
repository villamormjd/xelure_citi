import csv
from config import config
from .models import LoanData
from django.db.models import Sum
import re
import pdfplumber


def read_csv_file(file):
    file_data = file.read().decode("utf-8")
    lines = file_data.split("\n")
    headers = lines[0].split(",")
    indexes = dict()
    obj = []
    package_date = generate_package_date(file)
    for key, value in config["principal"].items():
        i = headers.index(value)
        indexes[key] = i

    for line in lines:
        line = line.split(",")
        try:
            obj.append(LoanData(
                package_date=package_date,
                transaction_id=line[indexes["transaction_id"]],
                investor_loan_number=line[indexes["investor_loan_number"]],
                insurance_fee=float(line[indexes["insurance_fee"]]),
                schedule_principal=float(line[indexes["schedule_principal"]]),
                curtailments=float(line[indexes["curtailments"]]),
                prepayment=float(line[indexes["prepayment"]]),
                liquidation_principal=float(line[indexes["liquidation_principal"]])
            ))
        except Exception as e:
            return str(e)

    return obj


def isLoanLevelDataExists(file):
    package_date = generate_package_date(file)
    llds = LoanData.objects.filter(package_date=package_date).count()
    print(llds)
    if llds:
        return True

    return False


def isFilePDF(file):
    if str(file).split(".")[1] == 'pdf':
        return True

    return False


def isFileCsv(file):

    if str(file).split(".")[1] == "csv":
        return True

    return False

def generate_package_date(file):
    file_name = str(file).split(".")[0][-4:]
    package_date = f"{file_name[:2]}-{file_name[2:]}"
    return package_date


def construct_meta(rows):
    conf = config["principal"].items()

    row = dict()
    total = 0
    for k,v in list(conf)[2:]:
        row[v] = rows.aggregate(Sum(f'{k}'))[f"{k}__sum"]
        if k == "liquidation_principal":
            row[v] = -(row[v])
        total += row[v]
    row["total"] = total

    for k, v in row.items(): row[k] = f"{v:,.2f}"
    return row


def extract_pdf(file):
    line_dict = dict()
    tolal_re = re.compile(r'.*Available:')
    line_re = re.compile(r'(.*?) (-?[\d,]+\.\d{2}) ((.*?) (-?[\d,]+\.\d{2}))?')
    doctype_re = r'(.*?\s.*?\s.*?)\s'
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages[5]
        text = pages.extract_text()
        doctype = None
        cat = None
        for t in text.split("\n")[5:]:
            if t.startswith("SOURCE"):
                cat = [x for x in re.split(r'(.*?\s.*?\s.*?)\s', t) if x][0].split()[0].lower()
                line_dict[cat] = dict()
            elif t.startswith("Interest Funds Available"):
                doctype = [x for x in re.split(doctype_re, t) if x][0]
                line_dict[cat][doctype] = dict()
                line_dict[cat][doctype]["items"] = []
                total = 0
            elif t.startswith("Principal Funds Available"):
                doctype = [x for x in re.split(doctype_re, t) if x][0]
                line_dict[cat][doctype] = dict()
                line_dict[cat][doctype]["items"] = []
                total = 0
            elif t.startswith("Other Funds Available"):
                doctype = [x for x in re.split(doctype_re, t) if x][0]
                line_dict[cat][doctype] = dict()
                line_dict[cat][doctype]["items"] = []
                total = 0
            elif t.startswith("Total Funds Available"):
                break
            elif tolal_re.search(t):
                continue
            else:
                t = t.replace('(', '-').replace(')', '')
                l = line_re.search(t)
                total += float(l.group(2).replace(",", ""))
                line_dict[cat][doctype]["total"] = f"{total:,.2f}"
                line_dict[cat][doctype]["items"].append({"key": l.group(1), "value": l.group(2)})
    return line_dict