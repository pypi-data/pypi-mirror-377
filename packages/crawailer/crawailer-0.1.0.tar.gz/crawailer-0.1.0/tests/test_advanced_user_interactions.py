"""
Advanced user interaction workflow test suite.

Tests complex multi-step user interactions, form workflows, drag-and-drop,
file uploads, keyboard navigation, and real-world user journey simulations.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestAdvancedUserInteractions:
    """Test complex user interaction workflows and patterns."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def interaction_config(self):
        """Browser configuration optimized for user interactions."""
        return BrowserConfig(
            headless=True,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (compatible; CrawailerTest/1.0)',
            slow_mo=50  # Slight delay for more realistic interactions
        )
    
    @pytest.fixture
    async def browser(self, interaction_config):
        """Browser instance for testing interactions."""
        browser = Browser(interaction_config)
        await browser.start()
        yield browser
        await browser.stop()

    # Multi-Step Form Workflows
    
    @pytest.mark.asyncio
    async def test_complex_form_workflow(self, base_url):
        """Test complex multi-step form submission workflow."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Step 1: Fill personal information
                const nameInput = document.querySelector('[data-testid="name-input"]');
                const emailInput = document.querySelector('[data-testid="email-input"]');
                const roleSelect = document.querySelector('[data-testid="role-select"]');
                
                nameInput.value = 'John Doe';
                emailInput.value = 'john.doe@example.com';
                roleSelect.value = 'developer';
                
                // Trigger input events
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                roleSelect.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Wait for validation
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Step 2: Check form validation
                const isFormValid = document.querySelector('[data-testid="submit-form-btn"]').disabled === false;
                
                // Step 3: Submit form
                if (isFormValid) {
                    document.querySelector('[data-testid="submit-form-btn"]').click();
                }
                
                // Step 4: Verify success notification
                await new Promise(resolve => setTimeout(resolve, 500));
                const notification = document.querySelector('[data-testid="notification"]');
                
                return {
                    step1_fieldsPopulated: {
                        name: nameInput.value,
                        email: emailInput.value,
                        role: roleSelect.value
                    },
                    step2_formValid: isFormValid,
                    step3_submitted: isFormValid,
                    step4_notificationShown: notification !== null && notification.textContent.includes('submitted'),
                    workflowComplete: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify each step
        assert result['step1_fieldsPopulated']['name'] == 'John Doe'
        assert result['step1_fieldsPopulated']['email'] == 'john.doe@example.com'
        assert result['step1_fieldsPopulated']['role'] == 'developer'
        assert result['step2_formValid'] is True
        assert result['step3_submitted'] is True
        assert result['workflowComplete'] is True
    
    @pytest.mark.asyncio
    async def test_conditional_form_logic(self, base_url):
        """Test forms with conditional logic and dynamic field visibility."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Create a mock form with conditional logic
                const formContainer = document.createElement('div');
                formContainer.innerHTML = `
                    <select id="userType" data-testid="user-type">
                        <option value="basic">Basic User</option>
                        <option value="premium">Premium User</option>
                        <option value="admin">Administrator</option>
                    </select>
                    <div id="conditionalFields" style="display: none;">
                        <input type="text" id="adminCode" data-testid="admin-code" placeholder="Admin Code">
                        <input type="text" id="department" data-testid="department" placeholder="Department">
                    </div>
                `;
                document.body.appendChild(formContainer);
                
                const userTypeSelect = document.getElementById('userType');
                const conditionalFields = document.getElementById('conditionalFields');
                
                // Add conditional logic
                userTypeSelect.addEventListener('change', (e) => {
                    if (e.target.value === 'admin') {
                        conditionalFields.style.display = 'block';
                    } else {
                        conditionalFields.style.display = 'none';
                    }
                });
                
                // Test workflow
                const workflow = [];
                
                // Step 1: Select basic user (fields should be hidden)
                userTypeSelect.value = 'basic';
                userTypeSelect.dispatchEvent(new Event('change'));
                workflow.push({
                    step: 'basic_user_selected',
                    fieldsVisible: conditionalFields.style.display !== 'none'
                });
                
                // Step 2: Select admin user (fields should be visible)
                userTypeSelect.value = 'admin';
                userTypeSelect.dispatchEvent(new Event('change'));
                workflow.push({
                    step: 'admin_user_selected',
                    fieldsVisible: conditionalFields.style.display !== 'none'
                });
                
                // Step 3: Fill admin fields
                const adminCodeInput = document.getElementById('adminCode');
                const departmentInput = document.getElementById('department');
                
                adminCodeInput.value = 'ADMIN123';
                departmentInput.value = 'Engineering';
                
                workflow.push({
                    step: 'admin_fields_filled',
                    adminCode: adminCodeInput.value,
                    department: departmentInput.value
                });
                
                // Cleanup
                document.body.removeChild(formContainer);
                
                return { workflow, success: true };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        workflow = result['workflow']
        assert len(workflow) == 3
        
        # Verify conditional logic
        assert workflow[0]['fieldsVisible'] is False  # Basic user - fields hidden
        assert workflow[1]['fieldsVisible'] is True   # Admin user - fields visible
        assert workflow[2]['adminCode'] == 'ADMIN123'
        assert workflow[2]['department'] == 'Engineering'
    
    @pytest.mark.asyncio
    async def test_form_validation_workflow(self, base_url):
        """Test progressive form validation and error handling."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Test progressive validation workflow
                const nameInput = document.querySelector('[data-testid="name-input"]');
                const emailInput = document.querySelector('[data-testid="email-input"]');
                
                const validationResults = [];
                
                // Step 1: Invalid name (too short)
                nameInput.value = 'A';
                nameInput.dispatchEvent(new Event('input'));
                await new Promise(resolve => setTimeout(resolve, 50));
                
                validationResults.push({
                    step: 'short_name',
                    nameValue: nameInput.value,
                    nameLength: nameInput.value.length,
                    isValidLength: nameInput.value.length >= 2
                });
                
                // Step 2: Valid name
                nameInput.value = 'Alice Johnson';
                nameInput.dispatchEvent(new Event('input'));
                await new Promise(resolve => setTimeout(resolve, 50));
                
                validationResults.push({
                    step: 'valid_name',
                    nameValue: nameInput.value,
                    nameLength: nameInput.value.length,
                    isValidLength: nameInput.value.length >= 2
                });
                
                // Step 3: Invalid email
                emailInput.value = 'invalid-email';
                emailInput.dispatchEvent(new Event('input'));
                await new Promise(resolve => setTimeout(resolve, 50));
                
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                validationResults.push({
                    step: 'invalid_email',
                    emailValue: emailInput.value,
                    isValidEmail: emailRegex.test(emailInput.value)
                });
                
                // Step 4: Valid email
                emailInput.value = 'alice.johnson@example.com';
                emailInput.dispatchEvent(new Event('input'));
                await new Promise(resolve => setTimeout(resolve, 50));
                
                validationResults.push({
                    step: 'valid_email',
                    emailValue: emailInput.value,
                    isValidEmail: emailRegex.test(emailInput.value)
                });
                
                // Step 5: Check overall form validity
                const overallValid = nameInput.value.length >= 2 && emailRegex.test(emailInput.value);
                validationResults.push({
                    step: 'overall_validation',
                    overallValid
                });
                
                return { validationResults, success: true };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        validation_results = result['validationResults']
        assert len(validation_results) == 5
        
        # Verify progressive validation
        assert validation_results[0]['isValidLength'] is False  # Short name
        assert validation_results[1]['isValidLength'] is True   # Valid name
        assert validation_results[2]['isValidEmail'] is False   # Invalid email
        assert validation_results[3]['isValidEmail'] is True    # Valid email
        assert validation_results[4]['overallValid'] is True    # Overall valid

    # Drag and Drop Interactions
    
    @pytest.mark.asyncio
    async def test_drag_and_drop_workflow(self, base_url):
        """Test drag and drop interactions and file handling."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Create drag and drop interface
                const container = document.createElement('div');
                container.innerHTML = `
                    <div id="dragSource" data-testid="drag-source" draggable="true" 
                         style="width: 100px; height: 50px; background: lightblue; margin: 10px;">
                        Drag Me
                    </div>
                    <div id="dropZone" data-testid="drop-zone"
                         style="width: 200px; height: 100px; background: lightgray; margin: 10px; border: 2px dashed gray;">
                        Drop Zone
                    </div>
                    <div id="status" data-testid="status">Ready</div>
                `;
                document.body.appendChild(container);
                
                const dragSource = document.getElementById('dragSource');
                const dropZone = document.getElementById('dropZone');
                const status = document.getElementById('status');
                
                let dragStarted = false;
                let dragEntered = false;
                let dropped = false;
                
                // Set up drag and drop event handlers
                dragSource.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', 'dragged-item');
                    dragStarted = true;
                    status.textContent = 'Drag started';
                });
                
                dropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                });
                
                dropZone.addEventListener('dragenter', (e) => {
                    e.preventDefault();
                    dragEntered = true;
                    dropZone.style.background = 'lightgreen';
                    status.textContent = 'Drag entered drop zone';
                });
                
                dropZone.addEventListener('dragleave', (e) => {
                    dropZone.style.background = 'lightgray';
                    status.textContent = 'Drag left drop zone';
                });
                
                dropZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    const data = e.dataTransfer.getData('text/plain');
                    dropped = true;
                    dropZone.style.background = 'lightcoral';
                    status.textContent = `Dropped: ${data}`;
                });
                
                // Simulate drag and drop
                const dragStartEvent = new DragEvent('dragstart', {
                    bubbles: true,
                    dataTransfer: new DataTransfer()
                });
                dragStartEvent.dataTransfer.setData('text/plain', 'dragged-item');
                
                const dragEnterEvent = new DragEvent('dragenter', {
                    bubbles: true,
                    dataTransfer: dragStartEvent.dataTransfer
                });
                
                const dropEvent = new DragEvent('drop', {
                    bubbles: true,
                    dataTransfer: dragStartEvent.dataTransfer
                });
                
                // Execute drag and drop sequence
                dragSource.dispatchEvent(dragStartEvent);
                await new Promise(resolve => setTimeout(resolve, 100));
                
                dropZone.dispatchEvent(dragEnterEvent);
                await new Promise(resolve => setTimeout(resolve, 100));
                
                dropZone.dispatchEvent(dropEvent);
                await new Promise(resolve => setTimeout(resolve, 100));
                
                const result = {
                    dragStarted,
                    dragEntered,
                    dropped,
                    finalStatus: status.textContent
                };
                
                // Cleanup
                document.body.removeChild(container);
                
                return result;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['dragStarted'] is True
        assert result['dragEntered'] is True
        assert result['dropped'] is True
        assert 'Dropped' in result['finalStatus']
    
    @pytest.mark.asyncio
    async def test_file_upload_simulation(self, base_url):
        """Test file upload workflows and file handling."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Create file upload interface
                const uploadContainer = document.createElement('div');
                uploadContainer.innerHTML = `
                    <input type="file" id="fileInput" data-testid="file-input" multiple accept=".txt,.jpg,.png">
                    <div id="fileDropZone" data-testid="file-drop-zone"
                         style="width: 300px; height: 150px; border: 2px dashed #ccc; padding: 20px; text-align: center;">
                        Drop files here or click to select
                    </div>
                    <div id="fileList" data-testid="file-list"></div>
                    <div id="uploadStatus" data-testid="upload-status">No files selected</div>
                `;
                document.body.appendChild(uploadContainer);
                
                const fileInput = document.getElementById('fileInput');
                const fileDropZone = document.getElementById('fileDropZone');
                const fileList = document.getElementById('fileList');
                const uploadStatus = document.getElementById('uploadStatus');
                
                let filesSelected = [];
                let filesDropped = [];
                
                // File selection handler
                const handleFiles = (files) => {
                    fileList.innerHTML = '';
                    uploadStatus.textContent = `${files.length} file(s) selected`;
                    
                    for (let file of files) {
                        const fileItem = document.createElement('div');
                        fileItem.textContent = `${file.name} (${file.size} bytes, ${file.type})`;
                        fileList.appendChild(fileItem);
                    }
                    
                    return files;
                };
                
                fileInput.addEventListener('change', (e) => {
                    filesSelected = Array.from(e.target.files);
                    handleFiles(filesSelected);
                });
                
                // Drag and drop for files
                fileDropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    fileDropZone.style.background = '#e6f3ff';
                });
                
                fileDropZone.addEventListener('dragleave', (e) => {
                    fileDropZone.style.background = 'transparent';
                });
                
                fileDropZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    fileDropZone.style.background = '#d4edda';
                    
                    if (e.dataTransfer.files) {
                        filesDropped = Array.from(e.dataTransfer.files);
                        handleFiles(filesDropped);
                    }
                });
                
                // Click handler for drop zone
                fileDropZone.addEventListener('click', () => {
                    fileInput.click();
                });
                
                // Simulate file upload workflow
                
                // Step 1: Create mock files
                const mockFile1 = new File(['Hello, World!'], 'hello.txt', { type: 'text/plain' });
                const mockFile2 = new File([''], 'image.jpg', { type: 'image/jpeg' });
                
                // Step 2: Simulate file selection
                Object.defineProperty(fileInput, 'files', {
                    value: [mockFile1, mockFile2],
                    writable: false
                });
                
                const changeEvent = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(changeEvent);
                
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Step 3: Simulate drag and drop
                const mockDataTransfer = {
                    files: [mockFile1, mockFile2]
                };
                
                const dropEvent = new DragEvent('drop', {
                    bubbles: true,
                    dataTransfer: mockDataTransfer
                });
                
                fileDropZone.dispatchEvent(dropEvent);
                
                await new Promise(resolve => setTimeout(resolve, 100));
                
                const result = {
                    filesSelectedCount: filesSelected.length,
                    filesDroppedCount: filesDropped.length,
                    fileListItems: fileList.children.length,
                    uploadStatus: uploadStatus.textContent,
                    fileDetails: filesSelected.length > 0 ? {
                        firstFileName: filesSelected[0].name,
                        firstFileSize: filesSelected[0].size,
                        firstFileType: filesSelected[0].type
                    } : null
                };
                
                // Cleanup
                document.body.removeChild(uploadContainer);
                
                return result;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['filesSelectedCount'] >= 2
        assert result['fileListItems'] >= 2
        assert 'file(s) selected' in result['uploadStatus']
        
        if result['fileDetails']:
            assert result['fileDetails']['firstFileName'] == 'hello.txt'
            assert result['fileDetails']['firstFileType'] == 'text/plain'

    # Keyboard Navigation and Accessibility
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation_workflow(self, base_url):
        """Test comprehensive keyboard navigation patterns."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Test keyboard navigation through form elements
                const formElements = [
                    document.querySelector('[data-testid="name-input"]'),
                    document.querySelector('[data-testid="email-input"]'),
                    document.querySelector('[data-testid="role-select"]'),
                    document.querySelector('[data-testid="submit-form-btn"]')
                ].filter(el => el !== null);
                
                const navigationResults = [];
                
                // Focus on first element
                if (formElements.length > 0) {
                    formElements[0].focus();
                    navigationResults.push({
                        step: 'initial_focus',
                        focusedElement: document.activeElement.getAttribute('data-testid'),
                        elementIndex: 0
                    });
                    
                    // Navigate through elements with Tab
                    for (let i = 1; i < formElements.length; i++) {
                        const tabEvent = new KeyboardEvent('keydown', {
                            key: 'Tab',
                            code: 'Tab',
                            keyCode: 9,
                            bubbles: true
                        });
                        
                        document.activeElement.dispatchEvent(tabEvent);
                        
                        // Manually focus next element (since we can't simulate real tab behavior)
                        formElements[i].focus();
                        
                        navigationResults.push({
                            step: `tab_navigation_${i}`,
                            focusedElement: document.activeElement.getAttribute('data-testid'),
                            elementIndex: i
                        });
                    }
                    
                    // Test Shift+Tab (reverse navigation)
                    const shiftTabEvent = new KeyboardEvent('keydown', {
                        key: 'Tab',
                        code: 'Tab',
                        keyCode: 9,
                        shiftKey: true,
                        bubbles: true
                    });
                    
                    document.activeElement.dispatchEvent(shiftTabEvent);
                    
                    // Manually focus previous element
                    if (formElements.length > 1) {
                        formElements[formElements.length - 2].focus();
                        navigationResults.push({
                            step: 'shift_tab_navigation',
                            focusedElement: document.activeElement.getAttribute('data-testid'),
                            elementIndex: formElements.length - 2
                        });
                    }
                }
                
                // Test Enter key on button
                const submitButton = document.querySelector('[data-testid="submit-form-btn"]');
                if (submitButton) {
                    submitButton.focus();
                    
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    });
                    
                    let enterPressed = false;
                    submitButton.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            enterPressed = true;
                        }
                    });
                    
                    submitButton.dispatchEvent(enterEvent);
                    
                    navigationResults.push({
                        step: 'enter_key_on_button',
                        enterPressed
                    });
                }
                
                // Test Escape key
                const escapeEvent = new KeyboardEvent('keydown', {
                    key: 'Escape',
                    code: 'Escape',
                    keyCode: 27,
                    bubbles: true
                });
                
                let escapePressed = false;
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') {
                        escapePressed = true;
                    }
                });
                
                document.dispatchEvent(escapeEvent);
                
                navigationResults.push({
                    step: 'escape_key',
                    escapePressed
                });
                
                return {
                    navigationResults,
                    totalElements: formElements.length,
                    keyboardAccessible: formElements.length > 0
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        navigation_results = result['navigationResults']
        assert len(navigation_results) >= 3
        assert result['keyboardAccessible'] is True
        
        # Verify navigation sequence
        for i, nav_result in enumerate(navigation_results):
            if nav_result['step'].startswith('tab_navigation'):
                assert 'focusedElement' in nav_result
                assert nav_result['elementIndex'] >= 0
    
    @pytest.mark.asyncio
    async def test_aria_and_screen_reader_simulation(self, base_url):
        """Test ARIA attributes and screen reader compatibility simulation."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Create accessible form elements
                const accessibleForm = document.createElement('div');
                accessibleForm.innerHTML = `
                    <h2 id="formTitle">User Registration Form</h2>
                    <form aria-labelledby="formTitle" role="form">
                        <div role="group" aria-labelledby="personalInfo">
                            <h3 id="personalInfo">Personal Information</h3>
                            <label for="accessibleName">
                                Full Name (required)
                                <input type="text" id="accessibleName" 
                                       aria-required="true" 
                                       aria-describedby="nameHelp"
                                       data-testid="accessible-name">
                            </label>
                            <div id="nameHelp" class="help-text">Enter your full legal name</div>
                            
                            <label for="accessibleEmail">
                                Email Address
                                <input type="email" id="accessibleEmail" 
                                       aria-describedby="emailHelp"
                                       data-testid="accessible-email">
                            </label>
                            <div id="emailHelp" class="help-text">We'll never share your email</div>
                        </div>
                        
                        <fieldset>
                            <legend>Notification Preferences</legend>
                            <label>
                                <input type="checkbox" value="email" data-testid="notify-email"> 
                                Email notifications
                            </label>
                            <label>
                                <input type="checkbox" value="sms" data-testid="notify-sms"> 
                                SMS notifications
                            </label>
                        </fieldset>
                        
                        <button type="submit" aria-describedby="submitHelp" data-testid="accessible-submit">
                            Register Account
                        </button>
                        <div id="submitHelp" class="help-text">Click to create your account</div>
                    </form>
                    
                    <div role="alert" id="statusAlert" aria-live="polite" data-testid="status-alert" 
                         style="display: none;">
                    </div>
                `;
                document.body.appendChild(accessibleForm);
                
                // Simulate screen reader analysis
                const analyzeAccessibility = () => {
                    const analysis = {
                        headingStructure: [],
                        labelsAndInputs: [],
                        ariaAttributes: [],
                        keyboardFocusable: [],
                        liveRegions: []
                    };
                    
                    // Analyze heading structure
                    const headings = accessibleForm.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    headings.forEach((heading, index) => {
                        analysis.headingStructure.push({
                            level: parseInt(heading.tagName.charAt(1)),
                            text: heading.textContent.trim(),
                            hasId: !!heading.id
                        });
                    });
                    
                    // Analyze labels and inputs
                    const inputs = accessibleForm.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => {
                        const label = accessibleForm.querySelector(`label[for="${input.id}"]`) || 
                                     input.closest('label');
                        
                        analysis.labelsAndInputs.push({
                            inputType: input.type || input.tagName.toLowerCase(),
                            hasLabel: !!label,
                            hasAriaLabel: !!input.getAttribute('aria-label'),
                            hasAriaLabelledby: !!input.getAttribute('aria-labelledby'),
                            hasAriaDescribedby: !!input.getAttribute('aria-describedby'),
                            isRequired: input.hasAttribute('required') || input.getAttribute('aria-required') === 'true'
                        });
                    });
                    
                    // Analyze ARIA attributes
                    const elementsWithAria = accessibleForm.querySelectorAll('[role], [aria-label], [aria-labelledby], [aria-describedby], [aria-live], [aria-required]');
                    elementsWithAria.forEach(element => {
                        analysis.ariaAttributes.push({
                            tagName: element.tagName.toLowerCase(),
                            role: element.getAttribute('role'),
                            ariaLabel: element.getAttribute('aria-label'),
                            ariaLabelledby: element.getAttribute('aria-labelledby'),
                            ariaDescribedby: element.getAttribute('aria-describedby'),
                            ariaLive: element.getAttribute('aria-live'),
                            ariaRequired: element.getAttribute('aria-required')
                        });
                    });
                    
                    // Analyze keyboard focusable elements
                    const focusableElements = accessibleForm.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    focusableElements.forEach(element => {
                        analysis.keyboardFocusable.push({
                            tagName: element.tagName.toLowerCase(),
                            type: element.type || null,
                            tabIndex: element.tabIndex,
                            hasVisibleLabel: !!element.textContent.trim() || !!element.value
                        });
                    });
                    
                    // Analyze live regions
                    const liveRegions = accessibleForm.querySelectorAll('[aria-live], [role="alert"], [role="status"]');
                    liveRegions.forEach(region => {
                        analysis.liveRegions.push({
                            role: region.getAttribute('role'),
                            ariaLive: region.getAttribute('aria-live'),
                            isVisible: region.style.display !== 'none'
                        });
                    });
                    
                    return analysis;
                };
                
                // Perform initial analysis
                const initialAnalysis = analyzeAccessibility();
                
                // Simulate user interaction with screen reader in mind
                const nameInput = accessibleForm.querySelector('[data-testid="accessible-name"]');
                const emailInput = accessibleForm.querySelector('[data-testid="accessible-email"]');
                const statusAlert = accessibleForm.querySelector('[data-testid="status-alert"]');
                
                // Fill form with validation feedback
                nameInput.value = 'Jane Smith';
                nameInput.dispatchEvent(new Event('input'));
                
                emailInput.value = 'jane.smith@example.com';
                emailInput.dispatchEvent(new Event('input'));
                
                // Simulate form submission and feedback
                statusAlert.textContent = 'Form validation successful. Ready to submit.';
                statusAlert.style.display = 'block';
                
                // Final analysis after interaction
                const finalAnalysis = analyzeAccessibility();
                
                const result = {
                    initialAnalysis,
                    finalAnalysis,
                    accessibilityScore: {
                        hasHeadingStructure: initialAnalysis.headingStructure.length > 0,
                        allInputsLabeled: initialAnalysis.labelsAndInputs.every(input => 
                            input.hasLabel || input.hasAriaLabel || input.hasAriaLabelledby
                        ),
                        hasAriaAttributes: initialAnalysis.ariaAttributes.length > 0,
                        hasKeyboardAccess: initialAnalysis.keyboardFocusable.length > 0,
                        hasLiveRegions: initialAnalysis.liveRegions.length > 0
                    }
                };
                
                // Cleanup
                document.body.removeChild(accessibleForm);
                
                return result;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        accessibility_score = result['accessibilityScore']
        
        assert accessibility_score['hasHeadingStructure'] is True
        assert accessibility_score['allInputsLabeled'] is True
        assert accessibility_score['hasAriaAttributes'] is True
        assert accessibility_score['hasKeyboardAccess'] is True
        assert accessibility_score['hasLiveRegions'] is True
        
        # Verify specific accessibility features
        initial_analysis = result['initialAnalysis']
        assert len(initial_analysis['headingStructure']) >= 2
        assert len(initial_analysis['labelsAndInputs']) >= 2
        assert len(initial_analysis['ariaAttributes']) >= 3

    # Complex Multi-Page Workflows
    
    @pytest.mark.asyncio
    async def test_multi_page_workflow_simulation(self, base_url):
        """Test complex workflows spanning multiple pages/views."""
        # Simulate a multi-step e-commerce workflow
        workflow_steps = []
        
        # Step 1: Product browsing
        content_step1 = await get(
            f"{base_url}/react/",
            script="""
                // Simulate product browsing page
                const products = [
                    { id: 1, name: 'Laptop', price: 999.99, category: 'Electronics' },
                    { id: 2, name: 'Mouse', price: 29.99, category: 'Electronics' },
                    { id: 3, name: 'Keyboard', price: 79.99, category: 'Electronics' }
                ];
                
                // Store products in sessionStorage (simulating navigation)
                sessionStorage.setItem('selectedProducts', JSON.stringify([]));
                sessionStorage.setItem('cart', JSON.stringify([]));
                
                // Simulate product selection
                const selectedProduct = products[0]; // Select laptop
                const selectedProducts = [selectedProduct];
                sessionStorage.setItem('selectedProducts', JSON.stringify(selectedProducts));
                
                return {
                    step: 'product_browsing',
                    productsAvailable: products.length,
                    selectedProduct: selectedProduct.name,
                    selectedProductPrice: selectedProduct.price,
                    navigationState: 'browsing'
                };
            """
        )
        
        workflow_steps.append(content_step1.script_result)
        
        # Step 2: Add to cart
        content_step2 = await get(
            f"{base_url}/vue/",
            script="""
                // Simulate cart page
                const selectedProducts = JSON.parse(sessionStorage.getItem('selectedProducts') || '[]');
                const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
                
                // Add selected products to cart
                selectedProducts.forEach(product => {
                    const cartItem = {
                        ...product,
                        quantity: 1,
                        subtotal: product.price
                    };
                    cart.push(cartItem);
                });
                
                sessionStorage.setItem('cart', JSON.stringify(cart));
                
                // Calculate cart totals
                const cartTotal = cart.reduce((total, item) => total + item.subtotal, 0);
                const cartQuantity = cart.reduce((total, item) => total + item.quantity, 0);
                
                return {
                    step: 'add_to_cart',
                    cartItems: cart.length,
                    cartTotal: cartTotal,
                    cartQuantity: cartQuantity,
                    navigationState: 'shopping_cart'
                };
            """
        )
        
        workflow_steps.append(content_step2.script_result)
        
        # Step 3: Checkout process
        content_step3 = await get(
            f"{base_url}/angular/",
            script="""
                // Simulate checkout page
                const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
                
                // Simulate checkout form completion
                const checkoutData = {
                    customerInfo: {
                        name: 'John Doe',
                        email: 'john.doe@example.com',
                        phone: '555-0123'
                    },
                    shippingAddress: {
                        street: '123 Main St',
                        city: 'Anytown',
                        state: 'CA',
                        zip: '12345'
                    },
                    paymentMethod: {
                        type: 'credit_card',
                        last4: '1234',
                        expiryMonth: '12',
                        expiryYear: '2025'
                    }
                };
                
                // Store checkout data
                sessionStorage.setItem('checkoutData', JSON.stringify(checkoutData));
                
                // Calculate final totals
                const subtotal = cart.reduce((total, item) => total + item.subtotal, 0);
                const tax = subtotal * 0.08; // 8% tax
                const shipping = subtotal > 50 ? 0 : 9.99; // Free shipping over $50
                const finalTotal = subtotal + tax + shipping;
                
                // Simulate order processing
                const orderId = 'ORD-' + Date.now();
                const orderData = {
                    orderId,
                    items: cart,
                    customer: checkoutData.customerInfo,
                    shipping: checkoutData.shippingAddress,
                    payment: checkoutData.paymentMethod,
                    totals: {
                        subtotal,
                        tax,
                        shipping,
                        total: finalTotal
                    },
                    orderDate: new Date().toISOString(),
                    status: 'confirmed'
                };
                
                sessionStorage.setItem('lastOrder', JSON.stringify(orderData));
                
                return {
                    step: 'checkout_complete',
                    orderId: orderId,
                    orderTotal: finalTotal,
                    itemsOrdered: cart.length,
                    customerName: checkoutData.customerInfo.name,
                    navigationState: 'order_confirmation'
                };
            """
        )
        
        workflow_steps.append(content_step3.script_result)
        
        # Verify complete workflow
        assert len(workflow_steps) == 3
        
        # Verify product browsing step
        step1 = workflow_steps[0]
        assert step1['step'] == 'product_browsing'
        assert step1['productsAvailable'] == 3
        assert step1['selectedProduct'] == 'Laptop'
        assert step1['selectedProductPrice'] == 999.99
        
        # Verify cart step
        step2 = workflow_steps[1]
        assert step2['step'] == 'add_to_cart'
        assert step2['cartItems'] == 1
        assert step2['cartTotal'] == 999.99
        assert step2['cartQuantity'] == 1
        
        # Verify checkout step
        step3 = workflow_steps[2]
        assert step3['step'] == 'checkout_complete'
        assert step3['orderId'].startswith('ORD-')
        assert step3['orderTotal'] > 999.99  # Should include tax
        assert step3['itemsOrdered'] == 1
        assert step3['customerName'] == 'John Doe'


class TestPerformanceOptimizedInteractions:
    """Test performance characteristics of complex user interactions."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_high_frequency_interactions(self, base_url):
        """Test performance with high-frequency user interactions."""
        content = await get(
            f"{base_url}/react/",
            script="""
                const startTime = performance.now();
                
                // Simulate rapid user interactions
                const interactions = [];
                const button = document.querySelector('[data-testid="increment-btn"]');
                
                if (button) {
                    // Perform 100 rapid clicks
                    for (let i = 0; i < 100; i++) {
                        const clickStart = performance.now();
                        button.click();
                        const clickEnd = performance.now();
                        
                        interactions.push({
                            interactionNumber: i + 1,
                            duration: clickEnd - clickStart
                        });
                        
                        // Small delay to prevent browser throttling
                        if (i % 10 === 0) {
                            await new Promise(resolve => setTimeout(resolve, 1));
                        }
                    }
                }
                
                const endTime = performance.now();
                const totalDuration = endTime - startTime;
                
                // Calculate performance metrics
                const averageInteractionTime = interactions.length > 0 ? 
                    interactions.reduce((sum, interaction) => sum + interaction.duration, 0) / interactions.length : 0;
                
                const maxInteractionTime = interactions.length > 0 ? 
                    Math.max(...interactions.map(i => i.duration)) : 0;
                
                const minInteractionTime = interactions.length > 0 ? 
                    Math.min(...interactions.map(i => i.duration)) : 0;
                
                return {
                    totalInteractions: interactions.length,
                    totalDuration,
                    averageInteractionTime,
                    maxInteractionTime,
                    minInteractionTime,
                    interactionsPerSecond: interactions.length / (totalDuration / 1000),
                    performanceGrade: averageInteractionTime < 10 ? 'A' : 
                                     averageInteractionTime < 50 ? 'B' : 
                                     averageInteractionTime < 100 ? 'C' : 'D'
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['totalInteractions'] == 100
        assert result['totalDuration'] > 0
        assert result['averageInteractionTime'] >= 0
        assert result['interactionsPerSecond'] > 0
        
        # Performance should be reasonable
        assert result['averageInteractionTime'] < 100  # Less than 100ms average
        assert result['performanceGrade'] in ['A', 'B', 'C', 'D']
    
    @pytest.mark.asyncio
    async def test_memory_efficient_interactions(self, base_url):
        """Test memory efficiency during complex interactions."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                const initialMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
                
                // Perform memory-intensive operations
                const data = [];
                
                // Create and manipulate large datasets
                for (let i = 0; i < 1000; i++) {
                    data.push({
                        id: i,
                        name: `Item ${i}`,
                        description: `Description for item ${i}`.repeat(10),
                        metadata: {
                            created: new Date(),
                            modified: new Date(),
                            tags: [`tag${i}`, `category${i % 10}`]
                        }
                    });
                    
                    // Simulate DOM updates
                    if (i % 100 === 0) {
                        window.testData.simulateUserAction('add-todo');
                    }
                }
                
                // Force garbage collection simulation
                if (window.gc) {
                    window.gc();
                }
                
                const peakMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
                
                // Clean up data
                data.length = 0;
                
                // Measure memory after cleanup
                const finalMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
                
                return {
                    initialMemory,
                    peakMemory,
                    finalMemory,
                    memoryIncrease: peakMemory - initialMemory,
                    memoryRecovered: peakMemory - finalMemory,
                    memoryEfficiency: finalMemory <= initialMemory * 1.5, // Within 50% of initial
                    dataItemsProcessed: 1000
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['dataItemsProcessed'] == 1000
        
        # Memory efficiency checks (if memory API is available)
        if result['initialMemory'] > 0:
            assert result['memoryIncrease'] >= 0
            assert result['peakMemory'] >= result['initialMemory']
            
            # Memory increase should be reasonable for the workload
            assert result['memoryIncrease'] < 100 * 1024 * 1024  # Less than 100MB increase


class TestErrorHandlingInInteractions:
    """Test error handling during complex user interactions."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_graceful_error_recovery(self, base_url):
        """Test graceful error handling and recovery in user workflows."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                const errorLog = [];
                
                // Set up global error handler
                const originalErrorHandler = window.onerror;
                window.onerror = (message, source, lineno, colno, error) => {
                    errorLog.push({
                        type: 'javascript_error',
                        message: message,
                        source: source,
                        line: lineno,
                        column: colno,
                        timestamp: Date.now()
                    });
                    return false; // Don't suppress the error
                };
                
                // Test error scenarios and recovery
                const testScenarios = [];
                
                // Scenario 1: Accessing non-existent element
                try {
                    const nonExistentElement = document.querySelector('#does-not-exist');
                    nonExistentElement.click(); // This will throw an error
                } catch (error) {
                    testScenarios.push({
                        scenario: 'non_existent_element',
                        errorCaught: true,
                        errorMessage: error.message,
                        recovered: true
                    });
                }
                
                // Scenario 2: Invalid JSON parsing
                try {
                    JSON.parse('invalid json');
                } catch (error) {
                    testScenarios.push({
                        scenario: 'invalid_json',
                        errorCaught: true,
                        errorMessage: error.message,
                        recovered: true
                    });
                }
                
                // Scenario 3: Type error in function call
                try {
                    const undefinedVar = undefined;
                    undefinedVar.someMethod();
                } catch (error) {
                    testScenarios.push({
                        scenario: 'type_error',
                        errorCaught: true,
                        errorMessage: error.message,
                        recovered: true
                    });
                }
                
                // Scenario 4: Promise rejection handling
                const promiseErrorScenario = await new Promise((resolve) => {
                    Promise.reject(new Error('Async operation failed'))
                        .catch(error => {
                            resolve({
                                scenario: 'promise_rejection',
                                errorCaught: true,
                                errorMessage: error.message,
                                recovered: true
                            });
                        });
                });
                
                testScenarios.push(promiseErrorScenario);
                
                // Test continued functionality after errors
                const continuedFunctionality = {
                    canAccessDOM: !!document.querySelector('body'),
                    canExecuteJS: (() => { try { return 2 + 2 === 4; } catch { return false; } })(),
                    canCreateElements: (() => { 
                        try { 
                            const el = document.createElement('div'); 
                            return !!el; 
                        } catch { 
                            return false; 
                        } 
                    })()
                };
                
                // Restore original error handler
                window.onerror = originalErrorHandler;
                
                return {
                    errorScenarios: testScenarios,
                    globalErrors: errorLog,
                    continuedFunctionality,
                    totalErrorsHandled: testScenarios.length,
                    allErrorsRecovered: testScenarios.every(scenario => scenario.recovered)
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['totalErrorsHandled'] >= 4
        assert result['allErrorsRecovered'] is True
        
        # Verify continued functionality after errors
        continued_functionality = result['continuedFunctionality']
        assert continued_functionality['canAccessDOM'] is True
        assert continued_functionality['canExecuteJS'] is True
        assert continued_functionality['canCreateElements'] is True
        
        # Verify specific error scenarios
        error_scenarios = result['errorScenarios']
        scenario_types = [scenario['scenario'] for scenario in error_scenarios]
        
        assert 'non_existent_element' in scenario_types
        assert 'invalid_json' in scenario_types
        assert 'type_error' in scenario_types
        assert 'promise_rejection' in scenario_types