## ADDED Requirements

### Requirement: Task Deletion Command
The system SHALL provide a CLI command to delete a task by task ID through the existing task API.

#### Scenario: Delete a task with explicit task ID
- **WHEN** a user runs `ctx tasks delete 9`
- **THEN** the system SHALL ask for explicit confirmation before sending the delete request
- **AND** the system SHALL call the task delete API for task `9`
- **AND** the system SHALL print a success message after the API confirms deletion

#### Scenario: Deletion rejected by API
- **WHEN** a user runs `ctx tasks delete 9`
- **AND** the API returns `403` or `404`
- **THEN** the system SHALL display the API error to the user
- **AND** the system SHALL exit without reporting success

#### Scenario: User cancels deletion
- **WHEN** a user runs `ctx tasks delete 9`
- **AND** the user declines the confirmation prompt
- **THEN** the system SHALL stop without calling the delete API
- **AND** the system SHALL print a cancellation message
