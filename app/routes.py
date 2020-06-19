from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ProjectForm, VendorForm, ResetPasswordRequestForm, ResetPasswordForm, AddTransactionForm, AddInvoiceForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Project, Vendor, ProjectTransaction, Invoice
from app.email import send_password_reset_email
from sqlalchemy import text

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/projects', methods=['GET','POST'])
@login_required
def projects():
    projects = Project.query.all()
    return render_template('projects.html', title='Projects', projects=projects)

@app.route('/vendors', methods=['GET',"POST"])
@login_required
def vendors():
    vendors = Vendor.query.all()
    return render_template('vendors.html', title='Vendors', vendors=vendors)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/add_vendor', methods=['GET','POST'])
def add_vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(name=form.name.data,
                        phone_number=form.phone_number.data,
                        email=form.email.data)
        db.session.add(vendor)
        db.session.commit()
        flash('Vendor Added')
        return redirect(url_for('vendors'))
    return render_template('add_vendor.html', form=form)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, budget=form.budget.data)
        db.session.add(project)
        db.session.commit()
        flash('Project Added')
        return redirect(url_for('projects'))
    return render_template('create_project.html', form=form)

@app.route('/vendors/<vendor_id>')
def vendor_page(vendor_id):
    vendor = Vendor.query.filter_by(id=vendor_id).first()
    return render_template('vendor_page.html', vendor=vendor)

@app.route('/projects/<project_id>')
def project_overview(project_id):
    transactions = ProjectTransaction.query.filter_by(project_id=project_id).join(Vendor).all()
    invoices = Invoice.query.filter_by(project_id=project_id).join(Vendor).all()
    project = Project.query.filter_by(id=project_id).first()
    total_spent_query = text('select sum(amount) from project_transactions where project_id = :project_id')
    project_spent = db.session.execute(total_spent_query, {'project_id': project_id}).first()[0]

    return render_template('project_overview.html', project=project, transactions=transactions, project_spent=project_spent,
                          invoices=invoices)

@app.route('/projects/<project_id>/add_transaction', methods=['GET', 'POST'])
def add_transaction(project_id):
    form = AddTransactionForm()
    project = Project.query.filter_by(id=project_id).first()
    if form.validate_on_submit():
        transaction = ProjectTransaction(project_id=project_id,
                                         vendor_id=Vendor.query.with_entities(Vendor.id).filter_by(name=form.vendor.data).first(),
                                         date=form.date.data,
                                         amount=form.amount.data,
                                         description=form.description.data)
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction Added')
        return redirect(url_for('project_overview', project_id=project.id))
    return render_template('add_transaction.html', project=project, form=form)

@app.route('/projects/<project_id>/add_invoice', methods=['GET', 'POST'])
def add_invoice(project_id):
    form = AddInvoiceForm()
    project = Project.query.filter_by(id=project_id).first()
    if form.validate_on_submit():
        invoice = Invoice(project_id=project_id,
                                         vendor_id=Vendor.query.with_entities(Vendor.id).filter_by(name=form.vendor.data).first(),
                                         invoice_date=form.invoice_date.data,
                                         paid_date=form.paid_date.data,
                                         amount=form.amount.data,
                                         description=form.description.data)
        db.session.add(invoice)
        db.session.commit()
        flash('Invoice Added')
        return redirect(url_for('project_overview', project_id=project.id))
    return render_template('add_invoice.html', project=project, form=form)




