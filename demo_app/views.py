from django.shortcuts import render, redirect
from .forms import InputForm
from .models import Customers
from datetime import date
from sklearn.externals import joblib
import numpy as np
from django.contrib.auth.decorators import login_required # 追加

# loaded_model = joblib.load('demo_app/demo_model.pkl')
loaded_model = joblib.load('/home/kurotsrrkk0513/kurotsrrkk0513.pythonanywhere.com/demo_app/demo_model.pkl')

@login_required # 追加
def index(request):
    return render(request, 'demo_app/index.html', {})

@login_required
def input_form(request):
    if request.method == "POST":
        form = InputForm(request.POST) # 入力データの取得
        if form.is_valid(): # Formの記載の検証
            form.save() # 入力を保存
            return redirect('result') # indexの関数の実行
    else:
        form = InputForm()
        return render(request, 'demo_app/input_form.html', {'form':form})

@login_required
def result(request):
    # 最新の登録者のデータを取得
    _data = Customers.objects.order_by('id').reverse().values_list\
        ('limit_balance', 'sex', 'education', 'marriage', 'age', 'pay_0', 'pay_2', 'pay_3', 'pay_4', 'pay_5', 'pay_6', 'bill_amt_1', 'pay_amt_1', 'pay_amt_2', 'pay_amt_3', 'pay_amt_4', 'pay_amt_5', 'pay_amt_6')

    # 推論の実行
    x = np.array([_data[0]])
    y = loaded_model.predict(x)
    _y_proba = loaded_model.predict_proba(x)
    y_proba = _y_proba * 100

    # 結果に基づいてコメントを返す
    if y[0] == 0:
        if y_proba[0][y[0]] > 75:
            comment = 'この方への貸し出しは危険です'
        else:
            comment = 'この方への貸し出しは要検討です'
    else:
        if y_proba[0][y[0]] > 75:
            comment = 'この方への貸し出しは全く問題ありません'
        else:
            comment = 'この方への貸し出しは問題ないでしょう'

    # 推論結果を保存
    _customer = Customers.objects.order_by('id').reverse()[0]
    _customer.proba = _y_proba[0][y[0]]
    _customer.result = y[0]
    _customer.comment = comment
    _customer.save()


    return render(request, 'demo_app/result.html', {'y':y[0], 'y_proba':round(y_proba[0][y[0]], 2), 'comment':comment}) # 推論結果をHTMLに渡す

@login_required
def history(request):
    if request.method == 'POST':
        d_id = request.POST
        d_customer = Customers.objects.filter(id=d_id['d_id'])
        d_customer.delete()
        customers = Customers.objects.all()
        return render(request, 'demo_app/history.html', {'customers':customers})

    else:
        customers = Customers.objects.all()
        return render(request, 'demo_app/history.html', {'customers':customers})
