"""
VibeGuard - Terraform Parser Engine
Parses .tf files into structured resource dictionaries using regex-based approach
for maximum compatibility (no hcl2 dependency issues).
"""

import re
import json
from typing import List, Dict, Optional


class TerraformParser:
    """
    Parses Terraform (.tf) files into structured resource dictionaries.
    Uses regex-based parsing for maximum compatibility.
    """

    def parse_file(self, content: str) -> List[Dict]:
        """Parse raw .tf content and return a list of resource dicts."""
        resources = []
        # Find all resource blocks
        resource_pattern = re.compile(
            r'resource\s+"(\w+)"\s+"(\w+)"\s*\{',
            re.MULTILINE
        )

        for match in resource_pattern.finditer(content):
            resource_type = match.group(1)
            resource_name = match.group(2)
            start = match.end()
            block_content = self._extract_block(content, start)

            resource = {
                "type": resource_type,
                "name": resource_name,
                "config": self._parse_block(block_content),
                "raw": block_content
            }
            resources.append(resource)

        return resources

    def _extract_block(self, content: str, start: int) -> str:
        """Extract content between matching braces."""
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
            i += 1
        return content[start:i - 1]

    def _parse_block(self, block: str) -> Dict:
        """Parse a block of terraform config into a dict of key-value pairs."""
        config = {}

        # Parse simple key = value pairs
        simple_kv = re.findall(
            r'^\s*(\w+)\s*=\s*(.+?)$',
            block,
            re.MULTILINE
        )
        for key, value in simple_kv:
            config[key] = self._parse_value(value.strip())

        # Parse nested blocks (like ingress {}, egress {})
        nested_pattern = re.compile(
            r'(\w+)\s*\{',
            re.MULTILINE
        )
        for match in nested_pattern.finditer(block):
            block_name = match.group(1)
            if block_name in ('jsonencode', 'resource', 'provider'):
                continue
            nested_start = match.end()
            nested_content = self._extract_block(block, nested_start)
            nested_config = self._parse_block(nested_content)

            if block_name not in config:
                config[block_name] = []
            if isinstance(config[block_name], list):
                config[block_name].append(nested_config)
            else:
                config[block_name] = [config[block_name], nested_config]

        # Check for jsonencode blocks (IAM policies)
        jsonencode_match = re.search(
            r'policy\s*=\s*jsonencode\((\{.*?\})\s*\)',
            block,
            re.DOTALL
        )
        if jsonencode_match:
            raw_json = jsonencode_match.group(1)
            config['_policy_raw'] = raw_json

        return config

    def _parse_value(self, value: str) -> any:
        """Parse a terraform value string."""
        # Remove quotes
        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        # Boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        # List
        if value.startswith('[') and value.endswith(']'):
            items = re.findall(r'"([^"]*)"', value)
            return items
        return value

    def get_resource_summary(self, resources: List[Dict]) -> Dict:
        """Return a summary of parsed resources."""
        summary = {}
        for r in resources:
            rtype = r['type']
            summary[rtype] = summary.get(rtype, 0) + 1
        return summary
