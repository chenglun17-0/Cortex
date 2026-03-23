## ADDED Requirements

### Requirement: Task Delete Entry In Web UI
The system SHALL provide a deletion entry for tasks in the Web UI with explicit confirmation before the delete request is sent.

#### Scenario: Delete task from detail page
- **WHEN** a user opens a task detail page
- **AND** the user confirms the delete action
- **THEN** the system SHALL call the task delete API for that task
- **AND** the system SHALL show a success notification
- **AND** the system SHALL navigate back to the task list page

#### Scenario: Delete task from task list page
- **WHEN** a user clicks delete on a task in the task list
- **AND** the user confirms the delete action
- **THEN** the system SHALL call the task delete API for that task
- **AND** the system SHALL remove the task from the refreshed list view

#### Scenario: User cancels deletion
- **WHEN** a user opens the delete confirmation dialog
- **AND** the user cancels the action
- **THEN** the system SHALL close the dialog
- **AND** the system SHALL NOT send a delete request

### Requirement: Task Delete Synchronization
The system SHALL synchronize task-related views after a successful deletion so deleted tasks disappear from Web task pages without a manual refresh.

#### Scenario: Refresh task-related caches after deletion
- **WHEN** a task is deleted successfully from the Web UI
- **THEN** the system SHALL invalidate the deleted task detail query
- **AND** the system SHALL invalidate task list queries
- **AND** the system SHALL invalidate project task / board queries that may contain the deleted task

#### Scenario: Open deleted task detail after deletion
- **WHEN** a user revisits a deleted task detail route
- **THEN** the system SHALL show the existing "task not found" experience

### Requirement: Task Delete Error Feedback
The system SHALL surface permission and existence errors from the delete API without falsely updating the UI.

#### Scenario: Delete task without permission
- **WHEN** a user confirms deletion in the Web UI
- **AND** the API returns `403`
- **THEN** the system SHALL show an error notification
- **AND** the task SHALL remain visible in the current view

#### Scenario: Delete missing task
- **WHEN** a user confirms deletion in the Web UI
- **AND** the API returns `404`
- **THEN** the system SHALL show an error notification
- **AND** the system SHALL keep the current UI consistent with the server response
