from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import login
from .models import LoanApplication, Loan, Transaction, Review, LoanStatus
from .forms import LoanApplicationForm, LoanForm, TransactionForm, ReviewForm, UserRegistrationForm

# View for Loan Application
def loan_application_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan_application = form.save(commit=False)
            loan_application.borrower = request.user  # Set the current logged-in user as the borrower
            loan_application.save()
            return redirect('loan_application_success')  # Redirect to a success page
    else:
        form = LoanApplicationForm()
    return render(request, 'loans/loan_application.html', {'form': form})

# Business Logic for Loan Approval (with eligibility checks)
@login_required
def approve_loan_view(request, application_id):
    application = get_object_or_404(LoanApplication, id=application_id)

    # Ensure only admins can approve loans
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to approve loans.", status=403)

    # Check if loan has already been processed
    if application.status != LoanStatus.PENDING:
        return HttpResponse("This loan has already been processed.", status=400)

    # Eligibility checks for loan approval
    if application.borrower.loan_applications.filter(status=LoanStatus.APPROVED).count() > 5:  # Borrower exceeds max loans
        return HttpResponse("The borrower has too many loans and is not eligible for this loan.", status=400)

    if application.borrower.loan_applications.filter(status=LoanStatus.REPAID).count() < 3:  # Borrower hasn't repaid enough loans
        return HttpResponse("The borrower hasn't repaid enough loans to qualify for this loan.", status=400)

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            # Proceed with loan approval
            loan = form.save(commit=False)
            loan.borrower = application.borrower  # Set borrower to the application borrower
            loan.status = LoanStatus.APPROVED  # Approve the loan
            loan.save()

            # Update the LoanApplication status to reflect the approval
            application.status = LoanStatus.APPROVED
            application.save()

            return redirect('loan_detail', loan_id=loan.id)
    else:
        form = LoanForm()  # Render the loan form for approval
    return render(request, 'loans/approve_loan.html', {'form': form, 'application': application})

# View for Transaction (payment/repayment)
def transaction_view(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.loan = loan  # Attach the transaction to the loan
            transaction.save()
            return redirect('transaction_success')
    else:
        form = TransactionForm()
    return render(request, 'loans/transaction.html', {'form': form, 'loan': loan})

# View for Review submission
def submit_review_view(request, user_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()  # Save the review
            return redirect('review_success')
    else:
        form = ReviewForm(initial={'reviewer': request.user.id})  # Set the current user as reviewer
    return render(request, 'loans/submit_review.html', {'form': form})

# User Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                return HttpResponse("Invalid role selected.", status=400)
            login(request, user)  # Log the user in immediately after registration
            return redirect('home')  # Redirect to the home page or dashboard
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# Role Checks
def is_lender(user):
    return user.groups.filter(name='Lender').exists()

def is_borrower(user):
    return user.groups.filter(name='Borrower').exists()

@login_required
@user_passes_test(is_lender)
def lender_dashboard(request):
    # Logic for lender dashboard
    return render(request, 'loans/lender_dashboard.html')

@login_required
@user_passes_test(is_borrower)
def borrower_dashboard(request):
    # Logic for borrower dashboard
    return render(request, 'loans/borrower_dashboard.html')

# Home View
def home(request):
    return render(request, 'loans/home.html')
