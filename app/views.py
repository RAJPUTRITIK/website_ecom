from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Product,cart,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# from django.shortcuts import render
# import razorpay
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponseBadRequest

class ProductView(View):
 def get(self,request):
  totalitem=0
  topwears=Product.objects.filter(category='TW')
  bottomwears=Product.objects.filter(category='BW')
  mobiles=Product.objects.filter(category='M')
  laptops=Product.objects.filter(category='L')
  if request.user.is_authenticated:
   totalitem=len(cart.objects.filter(user=request.user))
  return render(request,'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'laptops':laptops,'totalitem':totalitem})

class ProductDetailView(View):
 def get(self,request,pk):
  totalitem=0
  product=Product.objects.get(pk=pk)
  item_already_in_cart=False
  if request.user.is_authenticated:
    totalitem=len(cart.objects.filter(user=request.user))
    item_already_in_cart=cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
  return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
 if request.user.is_authenticated:
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    totalitem=len(cart.objects.filter(user=request.user))
    cart(user=user,product=product).save()
    
    return redirect('/cart',{'totalitem':totalitem})

@login_required
def show_cart(request):
 if request.user.is_authenticated:
  user=request.user
  c=cart.objects.filter(user=user)
  amount=0.0
  shipping_amount=70.0
  
  cart_product=[p  for p in cart.objects.all() if p.user == user]
  totalitem=len(cart.objects.filter(user=request.user)) 
  if cart_product:
    for p in cart_product:
      tempamount=(p.quantity * p.product.discount_price)
      amount+=tempamount
      totalamount=amount+shipping_amount
    return render(request,'app/addtocart.html',{'carts':c, 'totalamount':totalamount,'amount':amount,'totalitem':totalitem})
  else:
   return render(request,'app/emptycart.html')

def plus_cart(request):
 if request.method=="GET":
  prod_id=request.GET['prod_id']
  c=cart.objects.get(Q(product=prod_id) & Q(user=request.user))
  c.quantity+=1
  c.save()
  amount=0.0
  shipping_amount=70.0
  cart_product=[p  for p in cart.objects.all() if p.user == request.user]
  for p in cart_product:
    tempamount=(p.quantity * p.product.discount_price)
    amount+=tempamount
  data={
    'quantity':c.quantity,
    'amount':amount,
    'totalamount':amount+shipping_amount
    }
  return JsonResponse(data) #data pass krta hai jsonresponse object ke thor pe


def minus_cart(request):
 if request.method=="GET":
  prod_id=request.GET['prod_id']
  c=cart.objects.get(Q(product=prod_id) & Q(user=request.user))
  c.quantity-=1
  c.save()
  amount=0.0
  shipping_amount=70.0
  cart_product=[p  for p in cart.objects.all() if p.user == request.user]
  for p in cart_product:
    tempamount=(p.quantity * p.product.discount_price)
    amount+=tempamount

  data={
    'quantity':c.quantity,
    'amount':amount,
    'totalamount':amount+shipping_amount
    }
  return JsonResponse(data) #data pass krta hai jsonresponse object ke thor pe


def remove_cart(request):
 if request.method=="GET":
  prod_id=request.GET['prod_id']
  c=cart.objects.get(Q(product=prod_id) & Q(user=request.user))
  c.delete()
  amount=0.0
  shipping_amount=70.0
  cart_product=[p  for p in cart.objects.all() if p.user == request.user]
  for p in cart_product:
    tempamount=(p.quantity * p.product.discount_price)
    amount+=tempamount
  
  data={
    'quantity':c.quantity,
    'amount':amount,
    'totalamount':amount+shipping_amount
    }
  return JsonResponse(data) #data pass krta hai jsonresponse object ke thor pe




def buy_now(request):

 return render(request, 'app/buynow.html')



def address(request):
  add=Customer.objects.filter(user=request.user)
  return render(request, 'app/address.html',{'add':add ,'active':'btn-primary'})





def mobile(request,data=None):
 if data == None :
  mobiles=Product.objects.filter(category='M')
 elif data=='oppo' or data=='samsung':
  mobiles=Product.objects.filter(category='M').filter(brand=data)
 elif data=='below':
  mobiles=Product.objects.filter(category='M').filter(discount_price__gt=10000)
 elif data=='above':
  mobiles=Product.objects.filter(category='M').filter(discount_price__lt=10000)
 return render(request, 'app/mobile.html',{'mobiles':mobiles})

def laptop(request):
  if request.user.is_authenticated:
    lp=Product.objects.filter(category='L')
    totalitem=len(cart.objects.filter(user=request.user))
  return render(request,'app/laptop.html',{'lp':lp,'totalitem':totalitem})




def topwear(request):
  if request.user.is_authenticated:
    tps=Product.objects.filter(category='TW')
    totalitem=len(cart.objects.filter(user=request.user))
  return render(request,'app/topwear.html',{"tps":tps ,"totalitem":totalitem})

def bottomwear(request):
  if request.user.is_authenticated:
    btw=Product.objects.filter(category='BW')
    totalitem=len(cart.objects.filter(user=request.user))
  return render(request,'app/bottomwear.html',{'btw':btw,'totalitem':totalitem})

def login(request):
 return render(request, 'app/login.html')


class CustomerRegistrationView(View):
 def get(self,request):
  form=CustomerRegistrationForm()
  return render(request,'app/customerregistration.html',{'form':form})
 def post(self,request):
  form=CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request,'Congratulations!! Registered Successfully')
   form.save()
  return render(request,'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
 user=request.user
 add=Customer.objects.filter(user=user)
 cart_items=cart.objects.filter(user=user)
 amount=0.0
 shipping_amount=70.0
 cart_product=[p  for p in cart.objects.all() if p.user == request.user]
 if cart_items:
  for p in cart_product:
    tempamount=(p.quantity * p.product.discount_price)
    amount+=tempamount
  totalamount=amount+shipping_amount
 return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_items})

@login_required
def payment_done(request):
 user=request.user
 custid=request.GET.get('custid')
 customer=Customer.objects.get(id=custid)
 cart_item=cart.objects.filter(user=user)
 for c in cart_item:
  OrderPlaced(user=user,customer=customer, product=c.product, quantity=c.quantity).save()
  c.delete()
 return redirect("orders")

@login_required
def orders(request):
 op=OrderPlaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html',{'order_placed':op})

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
 def get(self,request):
  form=CustomerProfileForm()
  return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
 
 def post(self,request):
  form=CustomerProfileForm(request.POST)
  if form.is_valid():
   usr=request.user
   name=form.cleaned_data['name']
   locality=form.cleaned_data['locality']
   city=form.cleaned_data['city']
   state=form.cleaned_data['state']
   zipcode=form.cleaned_data['zipcode']
   reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
   reg.save()
   messages.success(request,'Congratulations!! Profile Updated Successfully') 
  return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
 



def search(request):
 if request.method=='GET':
  search=request.GET.get('search')
  post=Product.objects.all().filter(title=search)
 return render(request,'app/search.html',{'post':post})


#  if request.method=='POST':
#         data=request.POST['ser']
#         all_product=Product.objects.filter(Q(pname__icontains=data) | Q(desc__icontains=data))
#         return render(request,'shop.html',{'all_product':all_product})
#     else:
#         return redirect('shop')





# # authorize razorpay client with API Keys.
# razorpay_client = razorpay.Client(
#     auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# # # we need to csrf_exempt this url as
# # # POST request will be made by Razorpay
# # # and it won't have the csrf token.
# @csrf_exempt
# def paymenthandler(request):
#   # only accept POST request.
#   if request.method == "POST":
#       try:
          
#           # get the required parameters from post request.
#           payment_id = request.POST.get('razorpay_payment_id', '')
#           razorpay_order_id = request.POST.get('razorpay_order_id', '')
#           signature = request.POST.get('razorpay_signature', '')
#           params_dict = {
#               'razorpay_order_id': razorpay_order_id,
#               'razorpay_payment_id': payment_id,
#               'razorpay_signature': signature
#           }

#           # verify the payment signature.
#           result = razorpay_client.utility.verify_payment_signature(
#               params_dict)
#           if result is not None:
#               amount = 20000  # Rs. 200
#               try:

#                   # capture the payemt
#                   razorpay_client.payment.capture(payment_id, amount)

#                   # render success page on successful caputre of payment
#                   return render(request, 'paymentsuccess.html')
#               except:

#                   # if there is an error while capturing payment.
#                   return render(request, 'paymentfail.html')
#           else:

#               # if signature verification fails.
#               return render(request, 'paymentfail.html')
#       except:

#           # if we don't find the required parameters in POST data
#           return HttpResponseBadRequest()
#   else:
#       # if other than POST request is made.
#       return HttpResponseBadRequest()
    