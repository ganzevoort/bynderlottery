from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Draw, Ballot
from .forms import BallotPurchaseForm


class OpenDrawsListView(ListView):
    model = Draw
    template_name = "lottery/open_draws.html"
    context_object_name = "draws"

    def get_queryset(self):
        """Return all draws that haven't been closed yet"""
        return Draw.objects.filter(closed__isnull=True).order_by("date")


class ClosedDrawsListView(ListView):
    model = Draw
    template_name = "lottery/closed_draws.html"
    context_object_name = "draws"

    def get_queryset(self):
        """Return all draws that have been closed"""
        return Draw.objects.filter(closed__isnull=False).order_by("-date")


class UserBallotsView(LoginRequiredMixin, ListView):
    model = Ballot
    template_name = "lottery/user_ballots.html"
    context_object_name = "assigned_ballots"

    def get_queryset(self):
        """Return all ballots for the current user"""
        return self.request.user.account.ballots.filter(
            draw__isnull=False
        ).order_by("-draw__date", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add unassigned ballots (ballots without a draw)
        context["unassigned_ballots"] = (
            self.request.user.account.ballots.filter(draw__isnull=True)
        )
        # Add open draws for assignment
        context["open_draws"] = Draw.objects.filter(
            closed__isnull=True
        ).order_by("date")
        # Add purchase form
        context["purchase_form"] = BallotPurchaseForm()
        return context

    def post(self, request, *args, **kwargs):
        """Handle ballot purchase form submission"""
        form = BallotPurchaseForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]

            # Mock payment processing
            if self._process_mock_payment(form.cleaned_data):
                # Create unassigned ballots for the user
                for _ in range(quantity):
                    Ballot.objects.create(
                        account=request.user.account,
                        draw=None,  # Unassigned ballot
                    )
                if quantity == 1:
                    purchase = "a ballot"
                else:
                    purchase = f"{quantity} ballots"
                messages.success(
                    request,
                    f"Successfully purchased {purchase}! "
                    "You can now assign them to open draws.",
                )
            else:
                messages.error(request, "Payment failed. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")

        return redirect("lottery:user_ballots")

    def _process_mock_payment(self, payment_data):
        """Mock payment processing - always succeeds for demo purposes"""
        # In a real implementation, this would integrate with a payment
        # processor. For now, we'll simulate a successful payment
        import time

        time.sleep(0.5)  # Simulate processing time
        return True


class AssignBallotView(LoginRequiredMixin, View):
    def post(self, request, ballot_id):
        """Assign a ballot to a specific draw"""
        ballot = get_object_or_404(
            Ballot, id=ballot_id, account__user=request.user
        )
        draw_id = request.POST.get("draw_id")

        if not draw_id:
            messages.error(
                request, "Please select a draw to assign the ballot to."
            )
            return redirect("lottery:user_ballots")

        draw = get_object_or_404(Draw, id=draw_id, closed__isnull=True)

        if ballot.draw:
            messages.error(
                request, "This ballot is already assigned to a draw."
            )
        else:
            ballot.draw = draw
            ballot.save()
            messages.success(
                request,
                f"Ballot assigned to {draw.drawtype.name} on {draw.date}.",
            )

        return redirect("lottery:user_ballots")
