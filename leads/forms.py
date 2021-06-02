from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from agents.main_forms import UserCreationForm, UsernameField
from .models import Lead, Agent, Category, FollowUp, Company

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'age',
            'description',
            'phone_number',
            'email',
            'source',
            'profile_picture'
        )

    def queryset(self):    
        user = self.request.user
        org = self.request.user.userprofile
        agent = forms.ModelChoiceField(queryset=Agent.objects.filter(user_profile=org))
        self.fields["agent"].queryset = agent  
        return agent

    def clean_first_name(self):
        data = self.cleaned_data["first_name"]
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if Lead.objects.filter(email=data).exists():
            raise ValidationError("Lead already exists")
        return data

    def clean_phone(self):
        data = self.cleaned_data['phone_number']
        if Lead.objects.filter(phone_number=data).exists():
            raise ValidationError("Lead already exists")
        return data

    def clean(self):
        pass

    #def __init__(self,*args,**kwargs):
     #   request = kwargs.pop("request")
      #  super(LeadModelForm,self).__init__(*args,**kwargs)
       # agent = Agent.objects.filter(user_profile=request.user.userprofile)
        #self.fields["agent"]=agent

# class LeadForm(forms.Form):
#	first_name = forms.CharField()
#	last_name = forms.CharField()
#	age = forms.IntegerField()


class NewUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username","email")
        field_classes = {'username': UsernameField}

    def clean_email(self):
        data=self.cleaned_data["email"]
        if User.objects.filter(email=data).exists():
            raise ValidationError("Email already exists")
        return data

#class CompanyCreationForm(forms.ModelForm):
 #   class Meta:
  #      model = UserAccount
   #     fields = ("user_company",
    #        "user_company_address",
     #       "user_website")

    #def clean(self):
     #   data = self.cleaned_data["user_website"]
      #  if UserAccount.objects.filter(user_website=data).exists():
       #     raise ValidationError("Company already exists")
        #pass


class CompanyCreationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('company_name',
            'company_address',
            'company_phone',
            'company_website',
            'company_logo'
            )

    #def clean(self):
     #   pass


class BulkUploadForm(forms.Form):
    leads_file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(BulkUploadForm, self).__init__(*args, **kwargs)
        self.fields["leads_file"].widget.attrs.update(
            {
                "accept": ".csv",
            }
        )
        self.fields["leads_file"].required = True
        if self.data.get("leads_file"):
            self.fields["leads_file"].widget.attrs.update(
                {
                    "accept": ".csv",
                }
            )

    def clean_leads_file(self):
        document = self.cleaned_data.get("leads_file")
        if document:
            data = import_document_validator(document)
            if data.get("error"):
                raise forms.ValidationError(data.get("message"))
            else:
                self.validated_rows = data.get("validated_rows", [])
                self.invalid_rows = data.get("invalid_rows", [])
                if len(self.validated_rows) == 0:
                    raise forms.ValidationError(
                        "All the leads in the file are invalid."
                    )
        return document


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(user_profile=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'category',
        )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
        )


class FollowUpModelForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = (
            'notes',
            'file'
        )


#class LeadInvoiceModelForm(forms.ModelForm):
 #   class Meta:
  #      model = Lead_Invoice
   #     fields = (
    #        'date',
     #       'due_date',
      #      'status')

#class LeadLineItemModelForm(forms.ModelForm):
 #   class Meta:
  #      model= Lead_Line_Item
   #     fields = (
   #         'service',
    #        'description',
     #       'quantity',
      #      'rate')

#LeadLineItemFormSet = formset_factory(LeadLineItemModelForm, extra=1)



