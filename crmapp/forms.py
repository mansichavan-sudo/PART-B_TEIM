from django import forms
from .models import Product, customer_details, Inventory_add




class InventoryServiceForm(forms.Form):
    customer_id = forms.ModelChoiceField(
        queryset=customer_details.objects.all(),
        label="Customer ID",
        to_field_name='customerid',  # Ensure the field name is correct
        widget=forms.Select(attrs={'onchange': 'fetchCustomerName(this)'})
    )
    customer_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    sales_person_name = forms.CharField(max_length=255)
    p1 = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product 1")
    p1_quantity = forms.IntegerField(min_value=0, label="Quantity")
    p2 = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product 2", required=False)
    p2_quantity = forms.IntegerField(min_value=0, label="Quantity", required=False)
    p3 = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product 3", required=False)
    p3_quantity = forms.IntegerField(min_value=0, label="Quantity", required=False)
    p4 = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product 4", required=False)
    p4_quantity = forms.IntegerField(min_value=0, label="Quantity", required=False)




class InventoryAddForm(forms.ModelForm):
    class Meta:
        model = Inventory_add
        fields = ['product', 'quantity']


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category']
        labels = {
            'product_name': 'Product Name',
            'category': 'Select Category'
        }


class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category']
        labels = {
            'product_name': 'Product Name',
            'category': 'Select Category'
        }



from django import forms
from .models import WorkAllocation


class WorkAllocationForm(forms.ModelForm):
    class Meta:
        model = WorkAllocation
        fields = [
            'technician', 'fullname', 'customer_contact',
            'customer_address', 'gps_location', 'work_description',
            'customer_payment_status', 'payment_amount'
        ]



# class WorkAcceptRejectForm(forms.ModelForm):
#     class Meta:
#         model = WorkAllocation
#         fields = ['status']
#         widgets = {
#             'status': forms.RadioSelect(choices=[('Accepted', 'Accept'), ('Rejected', 'Reject')])
#         }






class LeadImportForm(forms.Form):
    file = forms.FileField()


class CustomerImportForm(forms.Form):
    file = forms.FileField()
    
# from django import forms
# from .models import followup

# class FollowUpForm(forms.ModelForm):
#     class Meta:
#         model = followup
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         stage = kwargs.pop('stage', 1)
#         super().__init__(*args, **kwargs)
#         # Enable only fields for the current stage
#         if stage == 1:
#             self.fields_to_show = ['havedonepestcontrolearlier', 'firstremark', 'secondfollowupdate']
#         elif stage == 2:
#             self.fields_to_show = ['secondremark', 'thirdfollowupdate']
#         elif stage == 3:
#             self.fields_to_show = ['thirdremark', 'fourthfollowupdate']
#         elif stage == 4:
#             self.fields_to_show = ['fourthremark']
        
#         for field in self.fields:
#             if field not in self.fields_to_show:
#                 self.fields[field].widget = forms.HiddenInput()



