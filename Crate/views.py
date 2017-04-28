from datetime import date

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render, get_list_or_404
from django.views.generic import View
from pinax.stripe.actions import customers, charges, invoices, subscriptions
from pinax.stripe.models import Plan, Subscription

from user_profile.models import Report
from user_profile.models import UserProfile
from .forms import DiscussionForm, ReportForm
from .middleware import has_active_subscription_with_plan
from .models import Category, SubCategory, InterestGroup, SellingCycle, Box, Item, Discussion, Vote

# Create your views here.

class BoxVoteFormView(View):
    item_name = {}

    def get(self, request, *args, **kwargs):
        BoxVoteFormView.item_name = {}
        curr_selling_cycle = SellingCycle.objects.filter(cycle_date__lte=date.today()).order_by('-cycle_date').first()
        box_vote = Box.objects.filter(sold_during=curr_selling_cycle, id=kwargs['box_id'])
        items = []
        for item in Item.objects.filter(contained_in=box_vote)[:4]:
            items.append(item)
            BoxVoteFormView.item_name[item.item_name] = item
        if len(items) == 0:
            box_width = 0
        else:
            box_width = 100 / len(items)
        return render(request, 'Crate/box_vote.html',
                      {'box_id': kwargs['box_id'],
                       'items': items,
                       'box_width': box_width})

    def post(self, request, *args, **kwargs):
        curr_selling_cycle = SellingCycle.objects.filter(cycle_date__lte=date.today()).order_by('-cycle_date').first()
        for name, item in BoxVoteFormView.item_name.items():
            # TODO: I am pretty sure this is not the right way to do it
            if request.POST.get(name) == '':
                item_vote, created = Vote.objects.get_or_create(selling_cycle=curr_selling_cycle, item=item)
                item_vote.vote_score += 1
                item_vote.save()
        return HttpResponseRedirect('')


def discussion_report_page(request, category_name, subcategory_name, interest_group_name):
    is_logged_in = request.user.is_authenticated()
    has_subscription = False
    has_default_payment_source = False
    # Check if the user is currently logged in
    # If yes: check if the user has an active subscription with the given interest group
    if is_logged_in:
        customer = customers.get_customer_for_user(request.user)
        plan = Plan.objects.get(name=interest_group_name)
        plan_id = plan.id
        has_subscription = has_active_subscription_with_plan(customer, plan_id)
        # Check if the user has a defaul payment source to charge if they choose to subscribe
        print("default source: ")
        print(customer.default_source)
        if (customer.default_source == ''):
            has_default_payment_source = False
        else:
            has_default_payment_source = True

    interest_group = InterestGroup.objects.get(interest_group_name=interest_group_name)
    discussions = Discussion.objects.filter(interest=interest_group).order_by('-pk')[:10]
    curr_selling_cycle = SellingCycle.objects.filter(cycle_date__lte=date.today()).order_by('-cycle_date').first()
    interest_group = InterestGroup.objects.get(interest_group_name=interest_group_name)
    box = Box.objects.filter(sold_during=curr_selling_cycle, type=interest_group).get()
    plan = Plan.objects.filter(name=interest_group_name)
    subscription_count = Subscription.objects.filter(plan_id=plan).count()
    print(subscription_count)
    if request.method == 'POST':
        user = UserProfile.objects.get(user=request.user)
        discussion_form = DiscussionForm(request.POST)
        if discussion_form.is_valid():
            comment = discussion_form.cleaned_data['comment']
            Discussion.objects.create(comment=comment, user=user, interest=interest_group)
            return HttpResponseRedirect('')
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.cleaned_data['report']
            Report.objects.create(report=report, user=user, box=box)
            return HttpResponseRedirect('')
    else:
        discussion_form = DiscussionForm()
        report_form = ReportForm()
    return render(request, 'Crate/box_discussion.html',
                  {'category_name': category_name,
                   'subcategory_name': subcategory_name,
                   'interest_group': interest_group,
                   'discussions': discussions,
                   'box': box,
                   'count': subscription_count,
                   'discussion_form': discussion_form,
                   'report_form': report_form,
                   'has_subscription': has_subscription,
                   'has_default_payment_source': has_default_payment_source})


def category_list(request):
    category_subcategory_map = {}
    for category in get_list_or_404(Category):
        changed = False
        for sub_category in SubCategory.objects.filter(category__category_name=category.category_name):
            if category_subcategory_map.get(category) is None:
                category_subcategory_map[category] = [sub_category]
            else:
                category_subcategory_map.get(category).append(sub_category)
            changed = True
        # Could just be done by checking len -- This just makes sure sub_category table is populated
        if not changed:
            category_subcategory_map[category] = []
    if len(category_subcategory_map) == 0:
        category_width = 0
    else:
        category_width = 100 / len(category_subcategory_map)
    return render(request, 'Crate/category_list.html',
                  {'category_map': category_subcategory_map,
                   'category_width': category_width})


def subcategory_list(request, category_name):
    subcategory_interest_map = {}
    for subcategory in get_list_or_404(SubCategory, category__category_name=category_name):
        changed = False
        for interest_group in InterestGroup.objects.filter(subcategory=subcategory):
            if subcategory_interest_map.get(subcategory) is None:
                subcategory_interest_map[subcategory] = [interest_group]
            else:
                subcategory_interest_map[subcategory].append(interest_group)
            changed = True
        if not changed:
            subcategory_interest_map[subcategory] = []
    if len(subcategory_interest_map) == 0:
        subcategory_width = 0
    else:
        subcategory_width = 100 / len(subcategory_interest_map)
    return render(request, 'Crate/subcategory_list.html',
                  {'category_name': category_name,
                   'subcategory': subcategory_interest_map,
                   'subcategory_width': subcategory_width})


def interest_group_list(request, category_name, subcategory_name):
    interest_groups = get_list_or_404(InterestGroup, subcategory__subcategory_name=subcategory_name)
    if len(interest_groups) == 0:
        interest_width = 0
    else:
        interest_width = 100 / len(interest_groups)
    return render(request, 'Crate/interest_group_list.html',
                  {'category_name': category_name,
                   'subcategory_name': subcategory_name,
                   'interest_groups': interest_groups,
                   'interest_width': interest_width})


def subscribe(request, category_name, subcategory_name, interest_group_name):
    print(interest_group_name)
    user = request.user
    customer = customers.get_customer_for_user(user)
    plan = Plan.objects.get(name=interest_group_name)
    plan_id = plan.stripe_id
    subscriptions.create(customer, plan_id)
    customers.sync_customer(customer)
    invoices.sync_invoices_for_customer(customer)
    charges.sync_charges_for_customer(customer)
    return redirect("box_discussion", category_name=category_name, subcategory_name=subcategory_name,
                    interest_group_name=interest_group_name)
