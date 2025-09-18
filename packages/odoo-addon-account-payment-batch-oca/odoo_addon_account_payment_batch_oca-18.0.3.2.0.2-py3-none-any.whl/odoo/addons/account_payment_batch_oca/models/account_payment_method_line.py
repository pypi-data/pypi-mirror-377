# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2014-2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    # For payment_order_ok, we don't define it as a related field
    # but as a computed field to allow to change the value on the
    # account.payment.method.line (useful to enable the option on a manual method)
    payment_order_ok = fields.Boolean(
        string="Selectable on Payment Orders",
        compute="_compute_payment_order_ok",
        store=True,
        readonly=False,
        precompute=True,
    )
    specific_sequence_id = fields.Many2one(
        "ir.sequence",
        check_company=True,
        copy=False,
        help="If left empty, the payment orders with this payment method will use the "
        "generic sequence for all payment orders.",
    )
    no_debit_before_maturity = fields.Boolean(
        string="Disallow Debit Before Maturity Date",
        default=True,
        help="If you activate this option on an Inbound payment method, "
        "you will have an error message when you confirm a debit order "
        "that has a payment line with a payment date before the maturity "
        "date.",
    )
    # Default options for the "payment.order.create" wizard
    default_payment_mode = fields.Selection(
        selection=[("same", "Same"), ("same_or_null", "Same or empty"), ("any", "Any")],
        string="Payment Method on Invoice",
        default="same",
    )
    default_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        compute="_compute_default_journal_ids",
        store=True,
        readonly=False,
        precompute=True,
        string="Journals Filter",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    default_invoice = fields.Boolean(
        string="Linked to an Invoice or Refund", default=False
    )
    default_target_move = fields.Selection(
        selection=[("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Journal Items",
        default="posted",
    )
    default_date_type = fields.Selection(
        selection=[("due", "Due"), ("move", "Move")],
        default="due",
        string="Type of Date Filter",
    )
    # default option for account.payment.order
    default_date_prefered = fields.Selection(
        selection=[
            ("now", "Immediately"),
            ("due", "Due Date"),
            ("fixed", "Fixed Date"),
        ],
        compute="_compute_default_date_prefered",
        store=True,
        readonly=False,
        precompute=True,
        string="Default Payment Execution Date",
    )
    group_lines = fields.Boolean(
        string="Group Transactions in Payment Orders",
        default=True,
        help="If this mark is checked, the transaction lines of the "
        "payment order will be grouped upon confirmation of the payment "
        "order.The grouping will be done only if the following "
        "fields matches:\n"
        "* Partner\n"
        "* Currency\n"
        "* Destination Bank Account\n"
        "* Payment Date\n"
        "and if the 'Communication Type' is 'Free'\n"
        "(other modules can set additional fields to restrict the "
        "grouping.)",
    )
    mail_notif = fields.Boolean(
        string="Notify by Email",
        help="If enabled, Odoo will automatically notify the partner by email when "
        "the payment/debit order file is successfully uploaded.",
    )
    mail_partner_policy = fields.Selection(
        [
            ("invoice_partner", "Partner of the Invoice"),
            ("last_payment", "Last Payment"),
            ("parent", "Parent Partner"),
            ("invoice_contact", "First Invoice Contact"),
            ("manual", "Manual"),
        ],
        string="Partner to Notify",
        default="invoice_partner",
        help="This configuration parameter will decide which partner "
        "is auto-configured as partner to notify on the payment/debit transaction. "
        "You can always manually change the partner to notify on the payment/debit "
        "transaction when the payment/debit order is in draft state.",
    )

    @api.depends("payment_method_id", "selectable")
    def _compute_payment_order_ok(self):
        for mode in self:
            payment_order_ok = mode.payment_method_id.payment_order_ok
            if not mode.selectable:
                payment_order_ok = False
            mode.payment_order_ok = payment_order_ok

    @api.depends("payment_method_id")
    def _compute_default_date_prefered(self):
        for line in self:
            if (
                line.payment_method_id.payment_type == "inbound"
                and line.payment_method_id.payment_order_ok
            ):
                line.default_date_prefered = "due"

    @api.depends("payment_method_id", "company_id")
    def _compute_default_journal_ids(self):
        ptype_map = {
            "outbound": "purchase",
            "inbound": "sale",
        }
        for line in self:
            if (
                line.payment_method_id
                and line.payment_method_id.payment_type in ptype_map
            ):
                line.default_journal_ids = list(
                    self.env["account.journal"]._search(
                        [
                            (
                                "type",
                                "=",
                                ptype_map[line.payment_method_id.payment_type],
                            ),
                            ("company_id", "=", line.company_id.id),
                        ]
                    )
                )

    @api.constrains("payment_order_ok", "selectable")
    def _check_payment_order_ok(self):
        for line in self:
            if line.payment_order_ok and not line.selectable:
                raise ValidationError(
                    _(
                        "Payment method '%(method)s' cannot be selectable on "
                        "payment/debit orders but not selectable on partners/invoices.",
                        method=line.display_name,
                    )
                )
