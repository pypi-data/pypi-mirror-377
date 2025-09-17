"""
Email Services for Technobits Library with SendInBlue Integration
"""

import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)


class SendInBlueService:
    """
    SendInBlue email service integration
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'SENDINBLUE_API_KEY', '')
        self.from_email = getattr(settings, 'TECHNOBITS_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        self.from_name = getattr(settings, 'TECHNOBITS_FROM_NAME', 'Technobits')
        
        # Initialize SendInBlue API client
        if self.api_key:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        else:
            self.api_instance = None
            logger.warning("SendInBlue API key not configured. Emails will be sent via Django's email backend.")
    
    def send_email(self, to_email: str, to_name: str, subject: str, html_content: str, 
                   text_content: str = None, template_params: Dict[str, Any] = None) -> bool:
        """
        Send email using SendInBlue API or fallback to Django email
        """
        try:
            if self.api_instance and self.api_key:
                return self._send_via_sendinblue(to_email, to_name, subject, html_content, text_content, template_params)
            else:
                return self._send_via_django(to_email, subject, html_content, text_content)
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_template_email(self, to_email: str, to_name: str, template_id: int, 
                           template_params: Dict[str, Any] = None) -> bool:
        """
        Send email using SendInBlue template
        """
        try:
            if not self.api_instance or not self.api_key:
                logger.error("SendInBlue not configured for template emails")
                return False
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                template_id=template_id,
                params=template_params or {}
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Template email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            return True
            
        except ApiException as e:
            logger.error(f"SendInBlue API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send template email to {to_email}: {e}")
            return False
    
    def _send_via_sendinblue(self, to_email: str, to_name: str, subject: str, 
                            html_content: str, text_content: str = None, 
                            template_params: Dict[str, Any] = None) -> bool:
        """
        Send email via SendInBlue API
        """
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={"name": self.from_name, "email": self.from_email},
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                params=template_params or {}
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            return True
            
        except ApiException as e:
            logger.error(f"SendInBlue API error: {e}")
            return False
    
    def _send_via_django(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Fallback to Django's email backend
        """
        try:
            send_mail(
                subject=subject,
                message=text_content or html_content,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False
            )
            logger.info(f"Email sent successfully to {to_email} via Django backend")
            return True
            
        except Exception as e:
            logger.error(f"Django email backend error: {e}")
            return False


class EmailService:
    """
    High-level email service for common authentication emails
    """
    
    def __init__(self):
        self.sendinblue = SendInBlueService()
        self.config = getattr(settings, 'TECHNOBITS_CONFIG', {}).get('EMAIL', {})
    
    def send_welcome_email(self, to_email: str, to_name: str, user_data: Dict[str, Any] = None) -> bool:
        """
        Send welcome email to new user
        """
        try:
            template_id = self.config.get('TEMPLATES', {}).get('WELCOME')
            
            if template_id:
                # Use SendInBlue template
                template_params = {
                    'name': to_name,
                    'email': to_email,
                    **(user_data or {})
                }
                return self.sendinblue.send_template_email(to_email, to_name, template_id, template_params)
            else:
                # Use custom HTML template
                subject = f"Welcome to {self.sendinblue.from_name}!"
                html_content = self._render_welcome_template(to_name, user_data)
                text_content = f"Welcome {to_name}! Thank you for joining {self.sendinblue.from_name}."
                
                return self.sendinblue.send_email(to_email, to_name, subject, html_content, text_content)
                
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {e}")
            return False
    
    def send_password_reset_email(self, to_email: str, to_name: str, reset_token: str, 
                                 reset_url: str = None) -> bool:
        """
        Send password reset email
        """
        try:
            template_id = self.config.get('TEMPLATES', {}).get('PASSWORD_RESET')
            
            if not reset_url:
                base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                reset_url = f"{base_url}/reset-password?token={reset_token}"
            
            if template_id:
                # Use SendInBlue template
                template_params = {
                    'name': to_name,
                    'email': to_email,
                    'reset_url': reset_url,
                    'reset_token': reset_token
                }
                return self.sendinblue.send_template_email(to_email, to_name, template_id, template_params)
            else:
                # Use custom HTML template
                subject = "Reset Your Password"
                html_content = self._render_password_reset_template(to_name, reset_url)
                text_content = f"Hi {to_name}, click this link to reset your password: {reset_url}"
                
                return self.sendinblue.send_email(to_email, to_name, subject, html_content, text_content)
                
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            return False
    
    def send_email_verification(self, to_email: str, to_name: str, verification_token: str,
                               verification_url: str = None) -> bool:
        """
        Send email verification email
        """
        try:
            template_id = self.config.get('TEMPLATES', {}).get('EMAIL_VERIFICATION')
            
            if not verification_url:
                base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                verification_url = f"{base_url}/verify-email?token={verification_token}"
            
            if template_id:
                # Use SendInBlue template
                template_params = {
                    'name': to_name,
                    'email': to_email,
                    'verification_url': verification_url,
                    'verification_token': verification_token
                }
                return self.sendinblue.send_template_email(to_email, to_name, template_id, template_params)
            else:
                # Use custom HTML template
                subject = "Verify Your Email Address"
                html_content = self._render_email_verification_template(to_name, verification_url)
                text_content = f"Hi {to_name}, click this link to verify your email: {verification_url}"
                
                return self.sendinblue.send_email(to_email, to_name, subject, html_content, text_content)
                
        except Exception as e:
            logger.error(f"Failed to send email verification to {to_email}: {e}")
            return False
    
    def _render_welcome_template(self, name: str, user_data: Dict[str, Any] = None) -> str:
        """
        Render welcome email HTML template
        """
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #4CAF50;">Welcome to {self.sendinblue.from_name}!</h1>
                <p>Hi {name},</p>
                <p>Thank you for joining {self.sendinblue.from_name}! We're excited to have you on board.</p>
                <p>You can now access all our features and start exploring.</p>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Best regards,<br>The {self.sendinblue.from_name} Team</p>
            </div>
        </body>
        </html>
        """
    
    def _render_password_reset_template(self, name: str, reset_url: str) -> str:
        """
        Render password reset email HTML template
        """
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #FF6B35;">Reset Your Password</h1>
                <p>Hi {name},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #FF6B35; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                <p>This link will expire in 24 hours for security reasons.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <p>Best regards,<br>The {self.sendinblue.from_name} Team</p>
            </div>
        </body>
        </html>
        """
    
    def _render_email_verification_template(self, name: str, verification_url: str) -> str:
        """
        Render email verification HTML template
        """
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2196F3;">Verify Your Email Address</h1>
                <p>Hi {name},</p>
                <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
                </div>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                <p>This verification link will expire in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
                <p>Best regards,<br>The {self.sendinblue.from_name} Team</p>
            </div>
        </body>
        </html>
        """


