name: 🚀 Feature Request
description: Suggest a new feature or enhancement
title: "[Feature] "
labels: [feature]
assignees: paulmagadi

body:
  - type: textarea
    id: description
    attributes:
      label: Describe the feature
      description: Clearly explain the feature and its purpose.
      placeholder: I want to implement a cart preview modal...
    validations:
      required: true

  - type: textarea
    id: implementation
    attributes:
      label: How would you implement it?
      description: Describe the components or files to change.
    validations:
      required: false

  - type: dropdown
    id: area
    attributes:
      label: Affected area
      options:
        - Backend
        - Frontend (Web)
        - Mobile (Flutter)
        - API
