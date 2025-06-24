import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Payment
import os
from django.conf import settings


def export_payments_to_excel(start_date=None, end_date=None, queryset=None):
    """
    Export payments to Excel file.
    
    Args:
        start_date (datetime, optional): Start date for filtering payments
        end_date (datetime, optional): End date for filtering payments
        queryset (QuerySet, optional): Custom queryset to export
        
    Returns:
        bytes: Excel file content
    """
    if queryset is None:
        queryset = Payment.objects.all()
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
    
    # Prepare data for Excel
    data = []
    for payment in queryset:
        data.append({
            'Transaction ID': payment.transaction_id,
            'Date': payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Amount': float(payment.amount),
            'Currency': payment.currency,
            'Status': payment.get_status_display(),
            'Payment Method': payment.payment_method.name,
            'Payment Category': payment.payment_category.name,
            'Payer ID': payment.payer_id,
            'Property ID': payment.property_id or '',
            'Notes': payment.notes or '',
            'Synced to QuickBooks': 'Yes' if payment.synced_to_quickbooks else 'No',
            'QuickBooks Reference': payment.quickbooks_ref or '',
            'Created By': payment.created_by.get_full_name() if payment.created_by else '',
            'Last Updated': payment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel writer
    output = pd.ExcelWriter('payments_export.xlsx', engine='xlsxwriter')
    df.to_excel(output, sheet_name='Payments', index=False)
    
    # Get workbook and worksheet objects
    workbook = output.book
    worksheet = output.sheets['Payments']
    
    # Add some formatting
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    # Write the column headers with the defined format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 15)  # Set column width
    
    # Set specific column widths
    worksheet.set_column('A:A', 20)  # Transaction ID
    worksheet.set_column('B:B', 20)  # Date
    worksheet.set_column('K:K', 30)  # Notes
    worksheet.set_column('L:L', 20)  # QuickBooks Reference
    
    # Add filters
    worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
    
    # Save the Excel file
    output.close()
    
    return output 


def append_payment_to_excel(payment):
    """
    Append a payment record to the physical Excel file.
    Creates the file if it doesn't exist.
    """
    excel_file_path = os.path.join(settings.BASE_DIR, 'financial_records.xlsx')
    
    # Prepare the payment data
    payment_data = {
        'Transaction ID': payment.transaction_id,
        'Date': payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'Amount': float(payment.amount),
        'Currency': payment.currency,
        'Status': payment.get_status_display(),
        'Payment Method': payment.payment_method.name,
        'Payment Category': payment.payment_category.name,
        'Payer ID': payment.payer_id,
        'Property ID': payment.property_id or '',
        'Notes': payment.notes or '',
        'Synced to QuickBooks': 'Yes' if payment.synced_to_quickbooks else 'No',
        'QuickBooks Reference': payment.quickbooks_ref or '',
        'Created By': payment.created_by.get_full_name() if payment.created_by else '',
        'Last Updated': payment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Create DataFrame for the new payment
    new_row = pd.DataFrame([payment_data])
    
    try:
        if os.path.exists(excel_file_path):
            # Read existing Excel file
            existing_df = pd.read_excel(excel_file_path)
            # Append new row
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        else:
            # Create new DataFrame if file doesn't exist
            updated_df = new_row
        
        # Save to Excel with formatting
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
            updated_df.to_excel(writer, sheet_name='Payments', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Payments']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Format headers
            for col_num, value in enumerate(updated_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
            
            # Set specific column widths
            worksheet.set_column('A:A', 20)  # Transaction ID
            worksheet.set_column('B:B', 20)  # Date
            worksheet.set_column('K:K', 30)  # Notes
            worksheet.set_column('L:L', 20)  # QuickBooks Reference
            
            # Add filters
            worksheet.autofilter(0, 0, len(updated_df), len(updated_df.columns) - 1)
            
    except Exception as e:
        # Log the error but don't raise it to prevent payment creation from failing
        print(f"Error appending to Excel file: {str(e)}")
        