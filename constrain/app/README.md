# ConStrain GUI

## Background
This tool builds workflows following the ConStrain API schema. The GUI provides the following:
- a graphical representation of their workflow 
- a layer of abstraction over the process of creating a workflow
- validation and submission of workflows

## How to Use

#### Selecting Basic or Advanced:

You can choose between Basic or Advanced settings in **Settings > Popup Settings**.

![Popup Settings](constrain/app/resources/constrain_gui_settings.png)

* **Basic** mode provides guided state creation and editing.
* **Advanced** mode allows manual editing of the full state definition.

#### Basic Form:

The Basic Form is designed to guide you through creating a state. It appears when you:

* Navigate to the **State** tab and press **Add Basic**, or
* Click a state in the Workflow Diagram while using **Basic** settings.

Steps to create a state with the Basic Form:

1. Choose a **State Type**.
2. If the type is **MethodCall**, continue with the following:

   * Choose the **Object Type** you want to initialize or call a method from.
   * Choose a **Method**.
   * Fill in all non-optional parameters.
   * (Optional) To add Payloads, click **Edit**. Add items using the **Name** and **Payload** fields and press **Add**. Right-click to delete an item. Click **OK** when finished.
3. Click **Save** to add the state to the Workflow Diagram.

For other state types:

1. Fill out the parameters provided.
2. To add **Choices**, click **Edit**. Add choices by selecting an **Object Type**, **Method**, **Object**, **Equals** value, and **Next** value, then click **Add**. Confirm by clicking **OK**.
3. Press **Save** to add the state to the Workflow Diagram.

#### Advanced Form:

The Advanced Form allows free-form editing with no guidance. It is used when:

* You press **Add Advanced** under the **State** tab, or
* Click a state in the Workflow Diagram while using **Advanced** settings.

You must enter the state manually in JSON format:

```json
{ 
  "name of state": {
    ...
  }
}
```

Make sure your state definition is valid before saving.

#### Meta Form:

Access the **Meta Form** by clicking on the **Meta** tab. This section allows you to define metadata for your workflow. You can enter the following information:

* **Workflow Name**
* **Author**
* **Date**
* **Version**
* **Description**

#### Imports Form:

Access the **Imports Form** by clicking on the **Imports** tab. This section allows you to include Python module imports used in your workflow.
To add an import:

* Type the import string (e.g., `numpy as np`)
* Click the **Add** button

To delete an import:

* Right-click the import in the list
* Select **Delete**

#### Workflow Diagram:

The **Workflow Diagram** is available under the **States** tab. You can add states to the diagram either by creating them manually or by importing a JSON file.

* **To create a state manually**, click **Add State**
* **To import states**, click **File** in the toolbar and select **Import Workflow**, then choose a JSON file.

##### Moving a State:

Drag and drop a state to move it.

##### Editing a State:

Click on a state to open its editor. The form shown depends on your current Popup Settings (Basic or Advanced).

##### Connecting States:

Click and drag from a control point on one state to a control point on another to create a connection.

##### Deleting States:

Right-click a state and select **Delete**.

##### Deleting Paths:

Right-click a path (line between states) and select **Delete**. If paths are difficult to click, zoom in for better precision.

##### Reformatting Diagram:

Click the **Rearrange** button in the far-right corner of the window to automatically organize the diagram into a tree-like layout.

#### Workflow Evaluation:

You can evaluate your workflow by clicking the **Evaluate Workflow** button at the bottom of the main window.
A popup will appear showing the submission results.

---

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