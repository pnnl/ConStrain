# ConStrain GUI

## Background
This tool builds workflows following the ConStrain API schema. The GUI provides the following:
- a graphical representation of their workflow 
- a layer of abstraction over the process of creating a workflow
- validation and submission of workflows

## How to Use

#### First Dialog:
When starting this GUI, a popup asks whether you want Basic or Advanced settings. The basic settings will let you to see the basic form when clicking on a state to edit it, while the advanced settings will let you see an advanced form.

#### Basic Form:
The basic form is meant to guide the user in the creation of a state. It is triggered by navigating to the 'State' tab and pressing the 'Add Basic' button, and also triggered by clicking a state in the Workflow Diagram while using Basic Settings. The following are the steps when creating a state from the basic popup:

1. Choose a state type
2. Continue reading these steps if 'MethodCall'. Else, go to the steps after the line below.
3. Choose the object type that you wish you initialize or that you want a method from
4. Choose a method
5. Fill out all non-optional parameters
6. If Payloads are to added, click 'Edit'. They can be added by filling out the 'Name:' and 'Payload:' forms and pressing 'Add', and deleted by right clicking a payload in the list widget. Finish by clicking OK.
7. Press the 'Save' button to add this state to the workflow diagram.
---
1. Fill out the parameters here.
2. To add choices, click 'Edit'. They can be added by selecting an 'Object Type', a 'Method', an 'Object', an 'Equals' value, adding a 'Next' value, and clicking add. This form will be added to the previous popup after you select 'OK'.
3. Press the 'Save' button to add this state to the workflow diagram.

#### Advanced Form:
The advanced form offers no guidance in the creation of a state. It is triggered by navigating to the 'State' tab and pressing the 'Add Advanced' button, and also triggered by clicking a state in the Workflow Diagram while using Advanced Settings. It is a text box where the user inputs a state. The state should be in the following format:

```json
 { 
    "name of state": {
        ...
    }
  }
```

#### Meta Form:
You can select the Meta Form by selecting the Meta tab. Here, you can add the following information to include in your workflow:
- Workflow Name
- Author
- Date
- Version
- Description

#### Imports Form:
You can select the Imports Form by selecting the Imports tab. Here, you can import Python modules to use inside of your workflow. To add to the Imports Form, simply type in the import, e.g. `numpy as np`, and press the 'Add' button. Imports can be deleted by right-clicking on an import in the list and pressing 'Delete'.

#### Workflow Diagram:
The Workflow Diagram can be accessed by navigating to the 'States' tab. States to add in your Workflow Diagram can either be created manually or imported. To create manually, you would select either the 'Add Basic' or 'Add Advanced' button. To import, you would click on the 'File' button in the toolbar and select 'Import' to find a JSON file to import.

##### Moving a State:
A state can be moved by dragging and dropping.

##### Editing a State:
A state can be edited by clicking it.

##### Connecting States:
A state can be connected to another state by first selecting a control point on a state, and then dragging and dropping to a control point on another state.

##### Deleting States:
A state can be deleted by right clicking on a state and selecting delete.

##### Deleting Paths:
A path can be deleted by right clicking on a path and selecting delete. Since paths quite small, it may be helpful to zoom-in in order to do this.

##### Reformatting Diagram:
To format your diagram into a tree-like shape, press the 'Reformat' button in the far right.

#### Workflow Validation:
Validating your workflow is necessary to be able to submit your workflow. To validate, press the 'Validate' button on the bottom of the main window. If the validation was successful, the 'Submit' button will turn active.

#### Workflow Submission:
To submit your workflow, press the 'Submit' button on the bottom of the main window. Note that the 'Submit' button is activated only after the workflow has been validated using the 'Validate' button. On submission of your workflow, a popup will be displayed showing the results.

## Files
The application contains 9 Python source files:

- `app`
- `import_form`
- `meta_form`
- `workflow_diagram`
- `popup_window`
- `advanced_popup`
- `list_and_choice_popups`
- `rect_connect`
- `submit`

#### app
This file runs the GUI. It is responsible for piecing together the main components of the app, like the meta form, the import form, and the workflow diagram. It also handles validate, import, and export functionalities. It contains 2 classes: 
- `GUI(QMainWindow)`: pieces classes together
- `UserSetting(QDialog)`: dialog to configure basic or advanced setting

#### import_form

This file contains the `ImportForm(QWidget)` class. This class is responsible for providing a form in which users can import Python modules to use in a workflow.

#### meta_form

This file contains the `MetaForm(QWidget)` class. This class is responsible for providing a form in which users can add meta information, such as author and workflow name.

#### workflow_diagram

This file is based on classes for organizing the UI of workflow visualization. It contains 2 classes:
- `Zoom(QGraphicsView)`: a view of the workflow diagram that includes a zoom feature
- `WorkflowDiagram(QWidget)`: node manager

#### popup_window
This file contains the `PopupWindow(QDialog)` class. This class handles the Basic Popup, which is a form that describes a state. It is responsible for handling the creation of a state and the import of a state.

#### advanced_popup
This file contains the `AdvancedPopup(QDialog)` class. This class handles the Advanced Popup, which is a text box that describes a state in JSON format. It is responsible for handling the creation of a state and the import of a state. The following is an example entry to this text box:

```json
  {
        "load data": {
            "Type": "MethodCall",
            "MethodCall": "DataProcessing",
            "Parameters": {
                "data_path": "./demo/api_demo/demo_dataset.csv",
                "data_source": "EnergyPlus"
            },
            "Payloads": {
                "data_processing_obj": "$"
            },
            "Start": "True",
            "Next": "slice data to get the first two months"
            }
    }
```

Note that this is slightly different than the format that is read by the API.

#### list_and_choice_popups
This file defines 2 classes to be used within Basic Popups:
- `ListPopup(QDialog)`: This class is used as a popup to define parameters in a Custom MethodCall and to define payloads in all MethodCalls.
- `ChoicesPopup(QDialog)`: This class is used as a popup to define choices.
#### rect_connect
This file contains the UI components that make up the workflow. It contains 4 classes:
- `Path(QGraphicsPathItem)`: paints path from a ControlPoint
- `ControlPoint(QGraphicsEllipseItem)`: points on a CustomItem that can connect to ControlPoints on other CustomItems
- `CustomItem(QGraphicsItem)`: shape on Scene representing a state
- `Scene(QGraphicsScene)`: scene to hold CustomItems, ControlPoints, and Paths

#### submit
This file allows for the submission of Workflows to the API. It contains 3 classes:
- `Worker(QThread)`: runs the workflow in the API
- `EmittingStream`: emits output of API to `SubmitPopup`
- `SubmitPopup(QDialog)`: popup that displays output of API when running the workflow