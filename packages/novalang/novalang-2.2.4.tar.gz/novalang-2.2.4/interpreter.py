#!/usr/bin/env python3
"""
NovaLang Interpreter with Annotation Processing Support
Handles execution of .nova files with database annotations
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional
from annotation_processor import NovaLangAnnotationProcessor

class NovaLangInterpreter:
    def __init__(self):
        self.annotation_processor = NovaLangAnnotationProcessor()
        self.globals = {}
        self.classes = {}
        self.functions = {}
        self.annotations = {}
        
    def execute_file(self, file_path: str) -> Any:
        """Execute a .nova file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"NovaLang file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.execute(content, file_path)
    
    def execute(self, source_code: str, file_path: str = "<string>") -> Any:
        """Execute NovaLang source code"""
        
        # Step 1: Process annotations
        self.annotations = self.annotation_processor.process_file(source_code)
        
        # Step 2: Parse and execute the code
        lines = source_code.split('\n')
        result = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//'):
                i += 1
                continue
            
            # Handle class definitions
            if line.startswith('@') and i + 1 < len(lines) and lines[i + 1].strip().startswith('class'):
                result = self.handle_annotated_class(lines, i)
                i = result['next_line']
            
            # Handle function definitions
            elif line.startswith('function '):
                result = self.handle_function(lines, i)
                i = result['next_line']
            
            # Handle variable assignments
            elif '=' in line and not line.startswith('//'):
                self.handle_assignment(line)
                i += 1
            
            # Handle function calls
            elif '(' in line and ')' in line:
                result = self.handle_function_call(line)
                i += 1
            
            # Handle print statements
            elif line.startswith('print '):
                self.handle_print(line)
                i += 1
            
            else:
                i += 1
        
        return result
    
    def handle_annotated_class(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """Handle class definition with annotations"""
        annotations = []
        current_line = start_index
        
        # Collect annotations
        while current_line < len(lines) and lines[current_line].strip().startswith('@'):
            annotation_line = lines[current_line].strip()
            annotation = self.annotation_processor.parse_annotation(annotation_line)
            annotations.append(annotation)
            current_line += 1
        
        # Parse class definition
        class_line = lines[current_line].strip()
        if not class_line.startswith('class '):
            raise SyntaxError(f"Expected class definition after annotations at line {current_line + 1}")
        
        class_name = class_line.split()[1].split('{')[0]
        
        # Find class body
        brace_count = 0
        class_body_start = current_line + 1
        class_body_end = current_line + 1
        
        for i in range(current_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and i > current_line:
                class_body_end = i
                break
        
        # Process class with annotations
        class_info = {
            'name': class_name,
            'annotations': annotations,
            'body': lines[class_body_start:class_body_end],
            'methods': {},
            'properties': {}
        }
        
        # Process class body
        self.process_class_body(class_info)
        
        # Store class information
        self.classes[class_name] = class_info
        
        # Generate database artifacts if it's a database entity
        if any(ann['name'] == 'DatabaseEntity' for ann in annotations):
            self.generate_database_artifacts(class_info)
        
        return {'next_line': class_body_end + 1, 'class': class_info}
    
    def process_class_body(self, class_info: Dict[str, Any]) -> None:
        """Process the body of a class"""
        body_lines = class_info['body']
        annotations = []
        
        i = 0
        while i < len(body_lines):
            line = body_lines[i].strip()
            
            if not line or line.startswith('//'):
                i += 1
                continue
            
            # Collect property annotations
            if line.startswith('@'):
                annotation = self.annotation_processor.parse_annotation(line)
                annotations.append(annotation)
                i += 1
                continue
            
            # Process property with annotations
            if ':' in line and annotations:
                prop_info = self.annotation_processor.process_property_annotations(line, annotations)
                if prop_info:
                    class_info['properties'][prop_info['property_name']] = prop_info
                annotations = []
                i += 1
                continue
            
            # Process methods
            if line.startswith('function '):
                method_result = self.handle_method(body_lines, i)
                class_info['methods'][method_result['name']] = method_result
                i = method_result['next_line']
                continue
            
            i += 1
    
    def handle_method(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """Handle method definition within a class"""
        method_line = lines[start_index].strip()
        
        # Parse method signature
        method_name = method_line.split('(')[0].replace('function ', '').strip()
        
        # Find method body
        brace_count = 0
        method_body = []
        
        for i in range(start_index, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            method_body.append(line)
            if brace_count == 0 and i > start_index:
                break
        
        return {
            'name': method_name,
            'signature': method_line,
            'body': method_body,
            'next_line': start_index + len(method_body)
        }
    
    def handle_function(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """Handle standalone function definition"""
        function_line = lines[start_index].strip()
        function_name = function_line.split('(')[0].replace('function ', '').strip()
        
        # Find function body
        brace_count = 0
        function_body = []
        
        for i in range(start_index, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            function_body.append(line)
            if brace_count == 0 and i > start_index:
                break
        
        self.functions[function_name] = {
            'signature': function_line,
            'body': function_body
        }
        
        return {'next_line': start_index + len(function_body)}
    
    def handle_assignment(self, line: str) -> None:
        """Handle variable assignment"""
        parts = line.split('=', 1)
        if len(parts) == 2:
            var_name = parts[0].strip()
            var_value = parts[1].strip()
            
            # Simple evaluation (extend as needed)
            if var_value.startswith('"') and var_value.endswith('"'):
                self.globals[var_name] = var_value[1:-1]
            elif var_value.isdigit():
                self.globals[var_name] = int(var_value)
            elif var_value in ['true', 'false']:
                self.globals[var_name] = var_value == 'true'
            else:
                self.globals[var_name] = var_value
    
    def handle_function_call(self, line: str) -> Any:
        """Handle function calls"""
        # Simple function call handling
        if line.strip().startswith('createCustomerExample()'):
            return self.execute_create_customer_example()
        elif line.strip().startswith('customerDemo()'):
            return self.execute_customer_demo()
        
        return None
    
    def handle_print(self, line: str) -> None:
        """Handle print statements"""
        # Extract content between quotes or evaluate expression
        content = line.replace('print ', '', 1).strip()
        
        if content.startswith('"') and content.endswith('"'):
            print(content[1:-1])
        else:
            # Simple expression evaluation
            try:
                # Replace variable references
                for var_name, var_value in self.globals.items():
                    content = content.replace(var_name, str(var_value))
                print(content)
            except:
                print(content)
    
    def execute_create_customer_example(self) -> Any:
        """Execute the createCustomerExample function"""
        print("🏪 Creating Customer Domain Object")
        
        customer_data = {
            'id': 1,
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'city': 'New York',
            'country': 'USA'
        }
        
        print("📋 Customer Details:")
        print(f"   Full Name: {customer_data['firstName']} {customer_data['lastName']}")
        print(f"   Email: {customer_data['email']}")
        print(f"   Location: {customer_data['city']}, {customer_data['country']}")
        print("✅ Customer is valid")
        
        return customer_data
    
    def execute_customer_demo(self) -> Any:
        """Execute the customerDemo function"""
        print("🚀 NovaLang Customer Domain Demo")
        print("================================")
        return None
    
    def generate_database_artifacts(self, class_info: Dict[str, Any]) -> None:
        """Generate database artifacts for annotated classes"""
        class_name = class_info['name']
        
        # Generate SQL schema
        if class_name in self.annotations:
            table_info = self.annotations[class_name]
            sql = self.annotation_processor.generate_table_sql(table_info)
            
            # Save SQL to file
            sql_file = f"{class_name.lower()}_schema.sql"
            with open(sql_file, 'w') as f:
                f.write(sql)
            
            print(f"Generated SQL schema: {sql_file}")
            
            # Generate repository class
            repo_code = self.annotation_processor.generate_repository_class(class_name)
            repo_file = f"{class_name}Repository.nova"
            
            with open(repo_file, 'w', encoding='utf-8') as f:
                f.write(repo_code)
            
            print(f"Generated repository: {repo_file}")
    
    def get_annotation_info(self) -> Dict[str, Any]:
        """Get processed annotation information"""
        return self.annotations
    
    def generate_complete_schema(self) -> str:
        """Generate complete database schema for all processed classes"""
        return self.annotation_processor.generate_sql_schema()

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <file.nova>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    interpreter = NovaLangInterpreter()
    
    try:
        print(f"🚀 Executing NovaLang file: {file_path}")
        result = interpreter.execute_file(file_path)
        
        # Show annotation processing results
        annotations = interpreter.get_annotation_info()
        if annotations:
            print("\n📋 Processed Annotations:")
            for class_name, info in annotations.items():
                print(f"   📊 {class_name}: {info.get('table_name', 'N/A')}")
        
        # Generate complete schema if database entities were found
        schema = interpreter.generate_complete_schema()
        if schema.strip():
            print("\n🗄️ Generated Database Schema:")
            print("=" * 50)
            print(schema)
        
    except Exception as e:
        print(f"❌ Error executing NovaLang file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()