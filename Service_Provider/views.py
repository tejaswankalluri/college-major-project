
from django.db.models import Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse
import numpy as np


import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

from sklearn.feature_extraction.text import CountVectorizer

from sklearn.tree import DecisionTreeClassifier
# model selection
from sklearn.metrics import confusion_matrix, accuracy_score, plot_confusion_matrix, classification_report

# Create your views here.
from Remote_User.models import ClientRegister_Model, deepfake_detection_type, detection_ratio, detection_accuracy


def serviceproviderlogin(request):
    if request.method == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password == "Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request, 'SProvider/serviceproviderlogin.html')


def View_Deepfake_Prediction_Ratio(request):
    detection_ratio.objects.all().delete()

    ratio = ""
    kword = 'FAKE'
    print(kword)
    obj = deepfake_detection_type.objects.all().filter(Q(Prediction=kword))
    obj1 = deepfake_detection_type.objects.all()
    count = obj.count()
    count1 = obj1.count()
    ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio1 = ""
    kword1 = 'REAL'
    print(kword1)
    obj1 = deepfake_detection_type.objects.all().filter(Q(Prediction=kword1))
    obj11 = deepfake_detection_type.objects.all()
    count1 = obj1.count()
    count11 = obj11.count()
    ratio1 = (count1 / count11) * 100
    if ratio1 != 0:
        detection_ratio.objects.create(names=kword1, ratio=ratio1)

    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Deepfake_Prediction_Ratio.html', {'objs': obj})


def View_Remote_Users(request):
    obj = ClientRegister_Model.objects.all()
    return render(request, 'SProvider/View_Remote_Users.html', {'objects': obj})


def ViewTrendings(request):
    topic = deepfake_detection_type.objects.values(
        'topics').annotate(dcount=Count('topics')).order_by('-dcount')
    return render(request, 'SProvider/ViewTrendings.html', {'objects': topic})


def charts(request, chart_type):
    chart1 = detection_ratio.objects.values(
        'names').annotate(dcount=Avg('ratio'))
    return render(request, "SProvider/charts.html", {'form': chart1, 'chart_type': chart_type})


def charts1(request, chart_type):
    chart1 = detection_accuracy.objects.values(
        'names').annotate(dcount=Avg('ratio'))
    return render(request, "SProvider/charts1.html", {'form': chart1, 'chart_type': chart_type})


def View_deepfake_prediction_Type(request):
    obj = deepfake_detection_type.objects.all()
    return render(request, 'SProvider/View_deepfake_prediction_Type.html', {'list_objects': obj})


def likeschart(request, like_chart):
    charts = detection_accuracy.objects.values(
        'names').annotate(dcount=Avg('ratio'))
    return render(request, "SProvider/likeschart.html", {'form': charts, 'like_chart': like_chart})


def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Data.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = deepfake_detection_type.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row.url, font_style)
        ws.write(row_num, 1, my_row.ipaddress, font_style)
        ws.write(row_num, 2, my_row.videoname, font_style)
        ws.write(row_num, 3, my_row.original_width, font_style)
        ws.write(row_num, 4, my_row.original_height, font_style)
        ws.write(row_num, 6, my_row.country, font_style)
        ws.write(row_num, 7, my_row.locale, font_style)
        ws.write(row_num, 8, my_row.latitude, font_style)
        ws.write(row_num, 9, my_row.longitude, font_style)
        ws.write(row_num, 10, my_row.Prediction, font_style)

    wb.save(response)
    return response


def train_model(request):
    detection_accuracy.objects.all().delete()
    data = pd.read_csv("Datasets.csv", encoding='latin-1')

    mapping = {'FAKE': 0, 'REAL': 1}

    data['Label'] = data['label'].map(mapping)

    x = data['url']
    y = data['Label']

    cv = CountVectorizer()

    print(x)
    print("Y")
    print(y)

    x = cv.fit_transform(x)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Naive Bayes")

    from sklearn.naive_bayes import MultinomialNB

    NB = MultinomialNB()
    NB.fit(X_train, y_train)
    predict_nb = NB.predict(X_test)
    naivebayes = accuracy_score(y_test, predict_nb) * 100
    print("ACCURACY")
    print(naivebayes)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_nb))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_nb))
    detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)

    # SVM Model
    print("SVM")
    from sklearn import svm

    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print("ACCURACY")
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression

    reg = LogisticRegression(
        random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    detection_accuracy.objects.create(
        names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

    print("Decision Tree Classifier")
    dtc = DecisionTreeClassifier()
    dtc.fit(X_train, y_train)
    dtcpredict = dtc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, dtcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, dtcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, dtcpredict))
    detection_accuracy.objects.create(
        names="Decision Tree Classifier", ratio=accuracy_score(y_test, dtcpredict) * 100)

    print("Gradient Boosting Classifier")
    from sklearn.ensemble import GradientBoostingClassifier
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(
        X_train,
        y_train)
    clfpredict = clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, clfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, clfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, clfpredict))
    models.append(('GradientBoostingClassifier', clf))
    detection_accuracy.objects.create(
        names="GradientBoostingClassifier", ratio=accuracy_score(y_test, clfpredict) * 100)

    labeled = 'Labeled_Data.csv'
    data.to_csv(labeled, index=False)
    data.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request, 'SProvider/train_model.html', {'objs': obj})
