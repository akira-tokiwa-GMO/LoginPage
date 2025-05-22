document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const passwordStrengthMeter = document.getElementById('password-strength-meter');

    if (!passwordInput || !passwordStrengthMeter) {
        // Elements not found, do nothing further
        // This can happen if the script is loaded on pages without these elements
        return;
    }

    passwordInput.addEventListener('input', function () {
        const password = passwordInput.value;
        let strength = 0;
        let feedbackText = 'Strength: ';

        // Criteria for strength
        // 1. Length (aligning with UserRegistrationSchema's min=8)
        if (password.length === 0) {
            feedbackText = ''; // No password, no feedback
            strength = -1; // Special case for empty
        } else if (password.length < 8) {
            feedbackText += 'Weak (too short)';
            strength = 1;
        } else if (password.length >= 8 && password.length <= 11) {
            feedbackText += 'Medium';
            strength = 2;
        } else { // >= 12
            feedbackText += 'Strong';
            strength = 3;
        }

        // 2. Presence of uppercase letters
        if (/[A-Z]/.test(password)) {
            strength++;
        }

        // 3. Presence of lowercase letters
        if (/[a-z]/.test(password)) {
            strength++;
        }

        // 4. Presence of numbers
        if (/[0-9]/.test(password)) {
            strength++;
        }

        // 5. Presence of special characters
        if (/[^A-Za-z0-9]/.test(password)) {
            strength++;
        }
        
        // Determine overall strength level and update meter text
        // Adjusting feedback text based on accumulated strength score
        if (strength === -1) { // Empty password
             passwordStrengthMeter.textContent = '';
             // Optional: Remove any strength classes if they were used
             // passwordStrengthMeter.className = 'password-strength-meter'; 
        } else if (strength < 2) { // Covers "Weak (too short)" if length < 8
            passwordStrengthMeter.textContent = feedbackText; // feedbackText already includes "Weak (too short)"
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-weak';
        } else if (strength <= 4) { // Still somewhat weak if only 1 or 2 criteria met beyond length
            passwordStrengthMeter.textContent = 'Strength: Weak';
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-weak';
        } else if (strength <= 6) { // Medium
            passwordStrengthMeter.textContent = 'Strength: Medium';
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-medium';
        } else if (strength <= 7) { // Strong
            passwordStrengthMeter.textContent = 'Strength: Strong';
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-strong';
        } else { // Very Strong (met all criteria and good length)
            passwordStrengthMeter.textContent = 'Strength: Very Strong';
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-very-strong';
        }

        // Special case for "Weak (too short)" to override general strength if length is the primary issue.
        if (password.length > 0 && password.length < 8) {
            passwordStrengthMeter.textContent = 'Strength: Weak (too short)';
            // Optional: passwordStrengthMeter.className = 'password-strength-meter strength-weak';
        }
    });
});
