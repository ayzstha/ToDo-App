from fasthtml.common import *

# Initialize the app
app, rt, todos, Todo = fast_app(
    'data/todos.db',
    hdrs=[Style(':root { --pico-font-size: 100%; }')],
    id=int, title=str, body=str, done=bool, due_date=str, tags=str, pk='id'
)

id_curr = 'current-todo'
def tid(id): return f'todo-{id}'

# Format a todo item for display
@patch
def __ft__(self: Todo):
    show = AX(self.title, f'/todos/{self.id}', id_curr)
    edit = AX('edit', f'/edit/{self.id}', id_curr)
    tags = f"Tags: {self.tags}" if self.tags else ""
    due = f" | Due: {self.due_date}" if self.due_date else ""
    done = ' ✅' if self.done else ''
    return Li(show, done, due, ' | ', tags, ' | ', edit, id=tid(self.id))

# Input for new todos
def mk_input(**kw): 
    return Group(
        Input(name="title", placeholder="Title", required=True, **kw),
        Textarea(name="body", placeholder="Details", required=True, **kw),
        Input(type="date", name="due_date", **kw),
        Input(name="tags", placeholder="Tags (comma-separated)", **kw),
    )

# Main page
@rt("/")
def get():
    add = Form(Group(mk_input(), Button("Add Task")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    card = Card(Ul(*todos(), id='todo-list'),
                header=add, footer=Div(id=id_curr)),
    title = 'ToDo Tracker'
    return Title(title), Main(H1(title), card, cls='container')

# Add a todo
@rt("/")
def post(todo: Todo): 
    return todos.insert(todo), mk_input(hx_swap_oob='true')

# Edit a todo
@rt("/edit/{id}")
def get(id: int):
    todo = todos.get(id)
    form = Form(
        Group(
            Input(value=todo.title, name="title"),
            Textarea(value=todo.body, name="body"),
            Input(value=todo.due_date, type="date", name="due_date"),
            Input(value=todo.tags, name="tags"),
            CheckboxX(todo.done, name="done", label="Completed"),
        ),
        Hidden(id="id"),
        Button("Save"),
        hx_put="/",
        hx_swap="outerHTML",
        target_id=tid(id),
    )
    return form

# Update a todo
@rt("/")
def put(todo: Todo): 
    return todos.upsert(todo), clear(id_curr)

# Delete a todo
@rt("/todos/{id}")
def delete(id: int):
    todos.delete(id)
    return clear(id_curr)

# View a todo
@rt("/todos/{id}")
def get(id: int):
    todo = todos.get(id)
    delete_btn = Button("Delete", hx_delete=f'/todos/{todo.id}', target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title, todo.body), delete_btn)

# Serve the app
serve()
