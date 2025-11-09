from django.contrib import admin
from django.urls import path,include
from crmapp import views , forms
from crm import settings
from django.conf.urls.static import static




urlpatterns = [
    path('index', views.index, name="index"),
    path('', views.landing_page),
    path('add-sales-person/', views.add_sales_person, name='add_sales_person'),
    path('sales-persons/', views.sales_person_list, name='sales_person_list'),
    path('edit-sales-person/<int:pk>/', views.edit_sales_person, name='edit_sales_person'),
    path('delete-sales-person/<int:pk>/', views.delete_sales_person, name='delete_sales_person'),
    path('sales-persons/export/', views.export_sales_person_csv, name='export_sales_person_csv'),
    path('customer_details_create',views.customer_details_create, name='customer_details_create'),
    path('service_management_create',views.service_management_create, name='service_management_create'),

     # Quotation Terms
    path('add_quotation_term/', views.add_quotation_term, name='add_quotation_term'),
    path('edit_quotation_term/<int:id>/', views.edit_quotation_term, name='edit_quotation_term'),
    path('view_quotation_terms/', views.view_quotation_terms, name='view_quotation_terms'),
    path('delete_quotation_term/<int:id>/', views.delete_quotation_term, name='delete_quotation_term'),

    # Invoice Terms
    path('add_invoice_term/', views.add_invoice_term, name='add_invoice_term'),
    path('edit_invoice_term/<int:id>/', views.edit_invoice_term, name='edit_invoice_term'),
    path('view_invoice_terms/', views.view_invoice_terms, name='view_invoice_terms'),
    path('delete_invoice_term/<int:id>/', views.delete_invoice_term, name='delete_invoice_term'),
    path('create_quotation/', views.quotation_management_create, name='create_quotation'),
    path('export-quotation/', views.export_quotation_excel, name='export_quotation'),
    path('save_quotation_session/', views.save_quotation_session, name='save_quotation_session'),
    # path('clear_quotation_session/', views.clear_quotation_session, name='clear_quotation_session'),



    # path('quotation_create',views.quotation_create, name='quotation_create'),
    path('invoice_create',views.invoice_create),
    # path('inventory_create',views.inventory_create),
    path('lead_management_create', views.lead_management_create, name='lead_management_create'),
    path('check_phone_number/', views.check_phone_number, name='check_phone_number'),
    path('followup/<int:lead_id>/', views.main_followup_view, name='main_followup_view'),
    path('today-work/', views.today_work, name='today_work'),
    path('pending-followups/', views.pending_followups, name='pending_followups'),




    path('signup', views.signup),
    path('user_login', views.user_login),
    path('logout', views.user_logout),
    path('display_customer', views.display_customer, name="display_customer"),
    path('import-customers/', views.import_customers, name='import_customers'),
    path('display_service_management', views.display_service_management, name="display_service_management"),
    path('display_allocation', views.display_allocation),
    path('display_quotation', views.display_quotation, name="display_quotation"),
    path('display_invoice', views.display_invoice),
    # Payment gateway
    path('checkout/', views.create_paypal_payment, name='create_paypal_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    # path('display_inventory', views.display_inventory),
    path('display_lead_management', views.display_lead_management, name='display_lead_management'),
    path('export-leads-excel/', views.export_leads_excel, name='export_leads_excel'), 
     # Make sure this line exists

    path('edit_customer/<rid>', views.edit_customer, name="edit_customer"),
    # this is for reschudle 
    path('edit_service_management/<rid>', views.edit_service_management, name='edit_service_management'),
    # this is for edit service record
    path('edit_service_records/<int:rid>/', views.edit_service_records, name='edit_service_records'),
    path('delete-service-product/<int:pid>/', views.delete_service_product, name='delete_service_product'),
    path('delete_service_records/<int:rid>/', views.delete_service_records , name='delete_service_records'),
    path('edit_quotation/<int:rid>', views.edit_quotation, name="edit_quotation"),
    path('edit_invoice/<rid>', views.edit_invoice),
    # path('edit_inventory/<rid>', views.edit_inventory),
    path('edit_lead_management/<rid>', views.edit_lead_management,name='edit_lead_management'),
    path('delete_customer/<rid>' ,views.delete_customer),
    path('delete_service_management/<rid>' ,views.delete_service_management),
    path('delete_quotation/<rid>' ,views.delete_quotation),
    # path('delete_invoice/<rid>' ,views.delete_invoice),
    # path('delete_inventory/<rid>' ,views.delete_inventory),
    path('delete_lead_management/<int:rid>' ,views.delete_lead_management),
    path('search',views.search), 
    path('search_inventory',views.search_inventory), 
    path('inventory_service/', views.inventory_service, name='inventory_service'),
    path('inventory_summary/', views.inventory_summary, name='inventory_summary'),
    # path('inventory_summary/<int:customer_id>/', views.inventory_summary, name='inventory_summary'),    
    path('add_product/', views.add_product, name='add_product'),
    path('update_product/<int:product_id>', views.update_product, name='update_product'),
    path('products/', views.product_list, name='product_list'),
    path('product-list/export/', views.export_product_list_csv, name='export_product_list_csv'),
    path('get_customer_name/', views.get_customer_name, name='get_customer_name'),
    path('create/', views.create_technician_profile, name='create_technician_profile'),
    path('technicians/', views.display_technician, name='display_technician'),
    path('technicians/edit/<int:technician_id>/', views.edit_technician, name='edit_technician'),
    path('technicians/delete/<int:technician_id>/', views.delete_technician, name='delete_technician'),
    path('technician_login/', views.technician_login, name='technician_login'), 
    path('not_authorized/', views.not_authorized, name='not_authorized'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('clear_notifications/',views.clear_notifications, name="clear_notifications"),
    path('create_superadmin/', views.create_superadmin, name='create_superadmin'),
    path('allocate/<int:service_id>/', views.allocate_work, name='allocate_work'),
    path('technician_work_list/', views.technician_work_list, name='technician_work_list'),
    path('handle_work/<int:allocation_id>/', views.handle_work_allocation, name='handle_work_allocation'),  
    path('work_allocation_success/', views.work_allocation_success, name='work_allocation_success'),
    path('pending_work/', views.pending_work, name='pending_work'),
    # path('accept_work/<int:work_id>/', views.accept_work, name='accept_work'),
    # path('reject_work/<int:work_id>/', views.reject_work, name='reject_work'),
    path('edit_work/<int:work_id>/', views.edit_work, name='edit_work'),
    path('delete_work/<int:work_id>/', views.delete_work, name='delete_work'),
    # path('work_list/', views.work_list, name='work_list'),
    path('work_list/', views.work_list_view, name='work_list'),
    # path('accept_work/<int:work_id>/', views.accept_work, name='accept_work'),
    # path('reject_work/<int:work_id>/', views.reject_work, name='reject_work'),
    path('complete_work/<int:work_id>/', views.complete_work, name='complete_work'),
    path('completed_work_list/', views.completed_work_list, name='completed_work_list'),
    path('work_details/<int:work_id>/', views.work_details, name='work_details'),
    path('completed_work/', views.AdminCompletedWorkView.as_view(), name='admin_completed_work'),
    path('work_detail/<int:pk>/', views.AdminWorkDetailView.as_view(), name='admin_work_details'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('get_products/', views.get_products_by_category, name='get_products_by_category'),
    path('importleads/', views.import_leads, name='import_leads'),
    path('quotation_history/<int:customer_id>/', views.quotation_history, name='quotation_history'),
    path('meeting-data/', views.meeting_data, name='meeting-data'),  # API endpoint for event data
    # path('user_login/', views.dashboard_view, name='dashboard'),
    path('user_login/', views.calendar_view, name='calendar_view'),
    path('go_towork/<int:work_id>/', views.go_towork, name='go_towork'),
    path('work/<int:work_id>/view_pdf/', views.view_work_pdf, name='view_work_pdf'),
    path('work/<int:work_id>/download_pdf/', views.download_work_pdf, name='download_work_pdf'),
    path('work/<int:work_id>/share_whatsapp/', views.generate_pdf_link, name='share_work_pdf_whatsapp'),
    path('get_customer_details/<str:customer_id>/', views.fetch_customer_details, name='get_customer_details'),
    path('get_service_details/<service_id>/', views.get_service_details, name='get_service_details'),
    path('get_quotation_details/<quotation_id>/', views.get_quotation_details, name='get_quotation_details'),
    path('get_invoice_details/<invoice_id>/', views.get_invoice_details, name='get_invoice_details'),
    path('get_lead_details/<lead_id>/', views.get_lead_details, name='get_lead_details'),
    path('get_allocation_details/<service_id>/', views.get_allocation_details, name='get_allocation_details'),  
    path('first_followup/<lead_id>/<int:next_stage>',views.firstfollowup_create, name='firstfollowup_create') ,
    path('second_followup/<lead_id>/<int:next_stage>',views.secondfollowup_create, name='secondfollowup_create') ,
    path('third_followup/<lead_id>/<int:next_stage>',views.thirdfollowup_create, name='thirdfollowup_create') ,
    path('final_followup/<lead_id>/<int:next_stage>',views.finalfollowup_create, name='finalfollowup_create') ,
    path('display_followup/',views.display_followup, name='display_followup') ,
    path('reschedule/<int:service_id>/', views.reschedule_create, name='reschedule_create'),
    path('display_reschedule/',views.display_reschedule, name='display_reschedule') ,
    path('branches/create/', views.create_branch, name='create_branch'),
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/edit/<int:branch_id>/', views.edit_branch, name='edit_branch'),
    path('branches/delete/<int:branch_id>/', views.delete_branch, name='delete_branch'),

    # path('generate_quotation/quotation/pdf/<int:id>/download', views.generate_quotation_pdf_download, name='download_quotation_pdf'),
    path('quotation/pdf/<int:id>/', views.reportlab_quotation_pdf, name='quotation_pdf'),
    path('generate_quotation/quotation/pdf/<int:id>/view',views.reportlab_quotation_pdf, name='view_quotation_pdf'),
    path('get_branch_details/<int:branch_id>/', views.get_branch_details, name='get_branch_details'),


    path('get_customer_details/', views.get_customer_details, name='get_customer_details'),
    path('export-customers/', views.export_customer_excel, name='export_customers'),
    path('get_quotation_details_by_no/', views.get_quotation_details_by_no, name='get_quotation_details_by_no'),

    # Bank Account 
    path('bank/create/', views.create_bank_account, name='create_bank_account'),
    path('bank/list/', views.list_bank_accounts, name='list_bank_accounts'),
    path('bank/edit/<int:account_id>/', views.edit_bank_account, name='edit_bank_account'),
    path('bank/delete/<int:account_id>/', views.delete_bank_account, name='delete_bank_account'),

    # Tax Invoice
    path('tax-invoice/create/',views.create_tax_invoice, name="create_tax_invoice"),
    path('tax-invoice/edit/<int:id>/',views.edit_tax_invoice, name="edit_tax_invoice"),
    path('display_tax_invoice/', views.display_tax_invoice, name="display_tax_invoice"),
    path('tax-invoice/pdf/<int:id>/', views.tax_invoice_pdf, name='tax_invoice_pdf'),
    path('export-invoice/', views.export_invoice_excel, name='export_invoice'),
    path('delete_invoice/<invoice_id>/', views.delete_invoice , name='delete_invoice'),


    # Payment Record Section
    path('ajax/fetch-invoice/', views.fetch_invoice_details, name='fetch_invoice'),
    path('payment-records/create/', views.create_payment_record, name='create_payment_records'),
    path('payment-records/list/',views.payment_records_list, name="payment_record_lists"),
    path('payment-records/details/<int:pk>',views.payment_records_details, name="payment_records_details"),
    path('fetch_invoice_product_details/<int:id>/', views.fetch_tax_invoice_details, name='fetch_invoice_product_details'),

    path('quotation/pdf/<int:id>/', views.reportlab_quotation_pdf, name='quotation_pdf'),
#    Message Templates
    path('message_templates', views.get_message_templates, name="message_templates"),
    path('edit_message_template/<int:id>/', views.edit_message_template, name='edit_message_template'),
    path('create_message_template/', views.create_message_template, name='create_message_template'),
    path('send-email/<int:pk>/', views.send_lead_email, name='send_lead_email'),
    path('send-group-email/<str:lead_type>/', views.send_group_lead_email, name='send_group_lead_email'),
    path('send-whatsapp/<int:pk>/', views.send_lead_whatsapp, name='send_lead_whatsapp'),
    path('send-group-whatsapp/<str:lead_type>/', views.send_group_lead_whatsapp, name='send_group_lead_whatsapp'),
    path('send-quotation-whatsapp/<int:id>/', views.send_quotation_pdf_on_whatsapp, name='send_quotation_pdf_on_whatsapp'),
    path('send-quotation-email/<int:id>/', views.send_quotation_email, name='send_quotation_email'),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
