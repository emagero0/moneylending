# loans/urls.py
from django.urls import path
from loans import views
from django.contrib.auth import views as auth_views

app_name = 'loans'

urlpatterns = [
    path('', views.home, name='home'),  # Homepage of the 'loans' app
    path('apply/', views.LoanView.as_view(), name='loan_application'),  # Loan application page
    path('list/', views.LoanListView.as_view(), name='loan_list'),  # List all loans
    path('detail/<int:pk>/', views.LoanDetailView.as_view(), name='loan_detail'),  # View details of a specific loan
    path('approve/<int:pk>/', views.approve_loan, name='approve_loan'),  # Approve or reject a loan
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('approve/<int:application_id>/', views.approve_loan_view, name='approve_loan'),
    path('transaction/<int:loan_id>/', views.transaction_view, name='transaction'),
    path('review/<int:user_id>/', views.submit_review_view, name='submit_review'),
    path('register/', views.register_view, name='register'),
    path('lender-dashboard/', views.lender_dashboard, name='lender_dashboard'),
    path('borrower-dashboard/', views.borrower_dashboard, name='borrower_dashboard'),
]
