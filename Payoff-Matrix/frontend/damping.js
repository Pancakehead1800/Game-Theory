// Keep the exact value and adjustable slider range in sync.
// Only the value is sent to Python; bounds are an editor preference.
export function setupDamping(onChange) {
  const valueInput = document.getElementById('damping-value');
  const slider = document.getElementById('damping-slider');
  const minimumInput = document.getElementById('damping-min');
  const maximumInput = document.getElementById('damping-max');
  const errorLabel = document.getElementById('damping-error');
  const inputs = [valueInput, minimumInput, maximumInput];

  function validate() {
    maximumInput.setCustomValidity('');
    let message = '';
    if (inputs.some(input => !input.checkValidity())) {
      message = 'Enter numbers between 0 and 1,000,000 for the value and bounds.';
    } else if (minimumInput.valueAsNumber >= maximumInput.valueAsNumber) {
      message = 'Maximum must be greater than minimum.';
      maximumInput.setCustomValidity(message);
    }
    errorLabel.textContent = message;
    slider.disabled = Boolean(message);
    for (const input of inputs) {
      input.setAttribute('aria-invalid', String(!input.validity.valid));
    }
    return !message;
  }

  function updateSlider() {
    slider.min = minimumInput.value;
    slider.max = maximumInput.value;
    slider.value = valueInput.value;
  }

  valueInput.addEventListener('input', () => {
    if (validate()) {
      const value = valueInput.valueAsNumber;
      if (value < minimumInput.valueAsNumber) minimumInput.value = value;
      if (value > maximumInput.valueAsNumber) maximumInput.value = value;
      updateSlider();
    }
    onChange();
  });

  function changeBounds() {
    if (validate()) {
      // If a bound excludes the current value, move it to the nearest endpoint.
      valueInput.value = Math.max(minimumInput.valueAsNumber,
        Math.min(maximumInput.valueAsNumber, valueInput.valueAsNumber));
      updateSlider();
    }
    onChange();
  }
  minimumInput.addEventListener('input', changeBounds);
  maximumInput.addEventListener('input', changeBounds);

  slider.addEventListener('input', () => {
    // Avoid exposing the slider's long floating-point decimals in the editor.
    const rounded = Number(Number(slider.value).toPrecision(2));
    valueInput.value = Math.max(minimumInput.valueAsNumber,
      Math.min(maximumInput.valueAsNumber, rounded));
    slider.value = valueInput.value;
    validate();
    onChange();
  });

  return function getDamping() {
    if (!validate()) {
      inputs.find(input => !input.validity.valid)?.reportValidity();
      throw new Error(errorLabel.textContent);
    }
    return valueInput.valueAsNumber;
  };
}
