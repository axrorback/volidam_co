from django.shortcuts import render , redirect , get_object_or_404
from .models import Address
from django.contrib.auth.decorators import login_required
from .forms import AddressForm

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)

    return render(request, "addresses/addresses.html", {
        "addresses": addresses
    })

@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True

            address.save()

            return redirect("address_list")

    else:
        form = AddressForm()

    return render(request, "addresses/address_create.html", {
        "form": form
    })

@login_required
def address_delete(request, pk):
    if request.method == "POST":
        address = get_object_or_404(
            Address,
            pk=pk,
            user=request.user
        )

        address.delete()

    return redirect("address_list")