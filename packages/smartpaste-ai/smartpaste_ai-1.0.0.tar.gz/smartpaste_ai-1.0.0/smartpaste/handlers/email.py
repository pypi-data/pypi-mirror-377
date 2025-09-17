"""
Email Detection and Analysis Handler for SmartPaste.

This handler detects email content (addresses, email text) and provides
parsing, validation, and enhancement features.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


class EmailHandler:
    """Handler for detecting and analyzing email content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the email handler.
        
        Args:
            config: Configuration dictionary for the handler.
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.logger = logging.getLogger(__name__)
        
        # Email patterns
        self.email_patterns = {
            "email_address": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "email_header": r'^(From|To|Cc|Bcc|Subject|Date|Reply-To):\s*(.+)$',
            "quoted_text": r'^>.*$',
            "signature": r'^--\s*$',
            "message_id": r'<[^@]+@[^>]+>',
            "thread_reference": r'(Re:|Fwd?:|RE:|FW:)',
        }
        
        # Common email domains for validation
        self.common_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'protonmail.com', 'zoho.com', 'fastmail.com',
            'company.com', 'organization.org', 'university.edu', 'government.gov'
        }
        
        # Email thread indicators
        self.thread_indicators = [
            'wrote:', 'On ', 'From:', 'Sent:', 'To:', 'Subject:',
            '-----Original Message-----', '--- Forwarded message ---',
            'Begin forwarded message:', '---------- Forwarded message ----------'
        ]
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process content to detect and analyze email.
        
        Args:
            content: The clipboard content to analyze.
            
        Returns:
            Dictionary with email analysis results or None if not email.
        """
        if not self.enabled:
            return None
        
        content = content.strip()
        if not content or len(content) < 5:
            return None
        
        # Check if content contains email-related information
        email_type = self._detect_email_type(content)
        if not email_type:
            return None
        
        try:
            result = {
                "original_content": content,
                "content_type": "email",
                "email_type": email_type,
            }
            
            if email_type == "email_addresses":
                result.update(self._process_email_addresses(content))
            elif email_type == "email_message":
                result.update(self._process_email_message(content))
            elif email_type == "email_thread":
                result.update(self._process_email_thread(content))
            
            result["enriched_content"] = self._generate_enriched_content(result)
            
            self.logger.info(f"Processed {email_type} content")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing email content: {e}")
            return None
    
    def _detect_email_type(self, content: str) -> Optional[str]:
        """Detect the type of email content."""
        # Check for multiple email addresses
        email_addresses = re.findall(self.email_patterns["email_address"], content)
        if len(email_addresses) >= 1:
            # Check if it's just email addresses or a full email
            if any(indicator in content for indicator in ['From:', 'To:', 'Subject:']):
                return "email_message"
            elif any(indicator in content for indicator in self.thread_indicators):
                return "email_thread"
            else:
                return "email_addresses"
        
        return None
    
    def _process_email_addresses(self, content: str) -> Dict[str, Any]:
        """Process content containing email addresses."""
        email_addresses = re.findall(self.email_patterns["email_address"], content)
        
        validated_emails = []
        for email in email_addresses:
            validation = self._validate_email(email)
            validated_emails.append({
                "address": email,
                "valid": validation["valid"],
                "domain": validation["domain"],
                "local_part": validation["local_part"],
                "domain_type": validation["domain_type"],
            })
        
        return {
            "email_addresses": validated_emails,
            "total_addresses": len(email_addresses),
            "unique_addresses": len(set(email_addresses)),
            "valid_addresses": sum(1 for e in validated_emails if e["valid"]),
            "domains": list(set(e["domain"] for e in validated_emails)),
        }
    
    def _process_email_message(self, content: str) -> Dict[str, Any]:
        """Process a full email message."""
        lines = content.split('\n')
        headers = {}
        body_start = 0
        
        # Parse headers
        for i, line in enumerate(lines):
            header_match = re.match(self.email_patterns["email_header"], line)
            if header_match:
                headers[header_match.group(1).lower()] = header_match.group(2).strip()
            elif line.strip() == "":
                body_start = i + 1
                break
        
        # Extract body
        body = '\n'.join(lines[body_start:]) if body_start < len(lines) else ""
        
        # Analyze email structure
        analysis = self._analyze_email_structure(body)
        
        return {
            "headers": headers,
            "body": body,
            "body_length": len(body),
            "structure": analysis,
            "sender": headers.get("from", ""),
            "recipients": self._parse_recipients(headers),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", ""),
            "attachments": self._detect_attachments(content),
        }
    
    def _process_email_thread(self, content: str) -> Dict[str, Any]:
        """Process an email thread or forwarded message."""
        # Split into individual messages
        messages = self._split_thread_messages(content)
        
        # Analyze each message
        analyzed_messages = []
        for i, message in enumerate(messages):
            msg_analysis = {
                "sequence": i + 1,
                "content": message,
                "length": len(message),
                "quoted_lines": len([line for line in message.split('\n') if line.startswith('>')]),
                "email_addresses": re.findall(self.email_patterns["email_address"], message),
            }
            analyzed_messages.append(msg_analysis)
        
        return {
            "thread_length": len(messages),
            "messages": analyzed_messages,
            "total_length": len(content),
            "participants": self._extract_thread_participants(content),
            "thread_subject": self._extract_thread_subject(content),
        }
    
    def _validate_email(self, email: str) -> Dict[str, Any]:
        """Validate an email address."""
        try:
            local_part, domain = email.split('@', 1)
            
            # Basic validation
            valid = (
                len(local_part) > 0 and len(local_part) <= 64 and
                len(domain) > 0 and len(domain) <= 253 and
                '.' in domain and
                not domain.startswith('.') and
                not domain.endswith('.') and
                not '..' in domain
            )
            
            # Determine domain type
            domain_type = self._classify_domain(domain)
            
            return {
                "valid": valid,
                "local_part": local_part,
                "domain": domain,
                "domain_type": domain_type,
            }
            
        except ValueError:
            return {
                "valid": False,
                "local_part": "",
                "domain": "",
                "domain_type": "invalid",
            }
    
    def _classify_domain(self, domain: str) -> str:
        """Classify the type of email domain."""
        domain_lower = domain.lower()
        
        if domain_lower in self.common_domains:
            return "personal"
        elif domain_lower.endswith(('.edu', '.ac.uk', '.uni', '.school')):
            return "educational"
        elif domain_lower.endswith(('.gov', '.mil')):
            return "government"
        elif domain_lower.endswith(('.org', '.ngo')):
            return "organization"
        elif domain_lower.endswith(('.com', '.net', '.biz', '.co')):
            return "commercial"
        else:
            return "other"
    
    def _analyze_email_structure(self, body: str) -> Dict[str, Any]:
        """Analyze the structure of an email body."""
        lines = body.split('\n')
        
        quoted_lines = [line for line in lines if line.startswith('>')]
        signature_start = -1
        
        # Find signature
        for i, line in enumerate(lines):
            if re.match(self.email_patterns["signature"], line.strip()):
                signature_start = i
                break
        
        return {
            "total_lines": len(lines),
            "quoted_lines": len(quoted_lines),
            "has_signature": signature_start != -1,
            "signature_start": signature_start,
            "original_text_lines": len(lines) - len(quoted_lines),
            "contains_urls": len(re.findall(r'https?://\S+', body)),
            "contains_phone": len(re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', body)),
        }
    
    def _parse_recipients(self, headers: Dict[str, str]) -> List[str]:
        """Parse all recipients from email headers."""
        recipients = []
        
        for field in ['to', 'cc', 'bcc']:
            if field in headers:
                # Split by comma and clean up
                field_recipients = [
                    addr.strip() for addr in headers[field].split(',')
                    if addr.strip()
                ]
                recipients.extend(field_recipients)
        
        return recipients
    
    def _detect_attachments(self, content: str) -> List[str]:
        """Detect mentions of attachments in email content."""
        attachment_indicators = [
            r'attachment', r'attached', r'attach', r'file',
            r'document', r'pdf', r'doc', r'image', r'photo',
            r'screenshot', r'please find', r'enclosed'
        ]
        
        attachments = []
        for indicator in attachment_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                attachments.append(indicator)
        
        return list(set(attachments))
    
    def _split_thread_messages(self, content: str) -> List[str]:
        """Split email thread into individual messages."""
        # Common thread separators
        separators = [
            r'-----Original Message-----',
            r'--- Forwarded message ---',
            r'Begin forwarded message:',
            r'---------- Forwarded message ----------',
            r'On .+ wrote:',
            r'From: .+',
        ]
        
        messages = [content]
        
        for separator in separators:
            new_messages = []
            for message in messages:
                parts = re.split(separator, message, flags=re.IGNORECASE)
                new_messages.extend([part.strip() for part in parts if part.strip()])
            messages = new_messages
        
        return messages[:10]  # Limit to prevent excessive processing
    
    def _extract_thread_participants(self, content: str) -> List[str]:
        """Extract all participants from an email thread."""
        participants = set()
        
        # Find all email addresses
        email_addresses = re.findall(self.email_patterns["email_address"], content)
        participants.update(email_addresses)
        
        # Look for names in From/To patterns
        name_patterns = [
            r'From:\s*([^<\n]+)',
            r'To:\s*([^<\n]+)',
            r'([^<\n]+)\s*<[^>]+>',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                clean_name = match.strip().strip('"\'')
                if clean_name and '@' not in clean_name:
                    participants.add(clean_name)
        
        return list(participants)
    
    def _extract_thread_subject(self, content: str) -> str:
        """Extract the subject from an email thread."""
        subject_match = re.search(r'Subject:\s*(.+)', content, re.IGNORECASE)
        if subject_match:
            return subject_match.group(1).strip()
        return ""
    
    def _generate_enriched_content(self, result: Dict[str, Any]) -> str:
        """Generate enriched version of the email content."""
        email_type = result["email_type"]
        
        if email_type == "email_addresses":
            return self._generate_address_summary(result)
        elif email_type == "email_message":
            return self._generate_message_summary(result)
        elif email_type == "email_thread":
            return self._generate_thread_summary(result)
        
        return result["original_content"]
    
    def _generate_address_summary(self, result: Dict[str, Any]) -> str:
        """Generate summary for email addresses."""
        addresses = result["email_addresses"]
        
        header = f"# Email Addresses ({result['total_addresses']} found)\n\n"
        
        valid_count = result["valid_addresses"]
        summary = (
            f"**Valid:** {valid_count}/{result['total_addresses']}\n"
            f"**Unique:** {result['unique_addresses']}\n"
            f"**Domains:** {', '.join(result['domains'])}\n\n"
        )
        
        address_list = "## Addresses:\n"
        for addr in addresses:
            status = "✅" if addr["valid"] else "❌"
            address_list += f"- {status} {addr['address']} ({addr['domain_type']})\n"
        
        return header + summary + address_list
    
    def _generate_message_summary(self, result: Dict[str, Any]) -> str:
        """Generate summary for email message."""
        headers = result["headers"]
        structure = result["structure"]
        
        header = "# Email Message\n\n"
        
        info = (
            f"**From:** {result['sender']}\n"
            f"**Subject:** {result['subject']}\n"
            f"**Date:** {result['date']}\n"
            f"**Recipients:** {len(result['recipients'])}\n"
            f"**Body Length:** {result['body_length']} characters\n\n"
        )
        
        struct_info = (
            f"**Structure:**\n"
            f"- Lines: {structure['total_lines']}\n"
            f"- Quoted: {structure['quoted_lines']}\n"
            f"- URLs: {structure['contains_urls']}\n"
            f"- Has Signature: {structure['has_signature']}\n\n"
        )
        
        return header + info + struct_info + f"**Body:**\n```\n{result['body']}\n```"
    
    def _generate_thread_summary(self, result: Dict[str, Any]) -> str:
        """Generate summary for email thread."""
        header = f"# Email Thread ({result['thread_length']} messages)\n\n"
        
        info = (
            f"**Subject:** {result['thread_subject']}\n"
            f"**Participants:** {', '.join(result['participants'][:5])}\n"
            f"**Total Length:** {result['total_length']} characters\n\n"
        )
        
        messages = "## Messages:\n"
        for msg in result['messages']:
            messages += (
                f"### Message {msg['sequence']}\n"
                f"- Length: {msg['length']} chars\n"
                f"- Quoted lines: {msg['quoted_lines']}\n"
                f"- Emails found: {len(msg['email_addresses'])}\n\n"
            )
        
        return header + info + messages