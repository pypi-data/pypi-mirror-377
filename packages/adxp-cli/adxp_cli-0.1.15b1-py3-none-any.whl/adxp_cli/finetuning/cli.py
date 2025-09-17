import click
from .training import (
    create_training,
    list_trainings,
    get_training,
    update_training,
    delete_training,
    get_training_status,
    start_training,
    stop_training,
)
from .metrics import (
    get_training_events,
    get_training_metrics,
    register_training_metrics,
)
from .trainer import (
    list_trainers,
    get_trainer,
    create_trainer,
    update_trainer,
    delete_trainer,
)
from .utils import (
    print_training_detail,
    print_training_list,
    print_trainer_detail,
    print_trainer_list,
    print_metrics_list,
    print_events_list,
)
from tabulate import tabulate
import json as json_module

@click.group()
def finetuning():
    """Command-line interface for AIP finetuning."""
    pass

# ====================================================================
# Training Commands
# ====================================================================

@finetuning.group()
def training():
    """Manage finetuning trainings."""
    pass

@training.command()
@click.option('--name', prompt=True, help='Training name')
@click.option('--dataset-ids', prompt=True, help='Comma-separated dataset IDs for training')
@click.option('--base-model-id', prompt=True, help='Base model ID for fine-tuning')
@click.option('--trainer-id', prompt=True, help='Trainer ID for the training')
@click.option('--resource', prompt=True, help='Resource configuration as JSON string (e.g., {"cpu_quota": 4, "mem_quota": 8, "gpu_quota": 1, "gpu_type": "H100"})')
@click.option('--params', prompt=True, help='Training parameters as string (e.g., "learning_rate=0.001\\nepochs=10\\nbatch_size=32")')
@click.option('--description', default='', help='Training description')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Training creation JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def create(name, dataset_ids, base_model_id, trainer_id, resource, params, description, json_path, json_output):
    """Create a new training.
    
    \b
    ** params field's examples **
    Training Parameters (--params):
    [TrainingConfig]
    use_lora = true              # LoRA fine-tuning (true) or full fine-tuning (false). Default: true
    num_train_epochs = 1         # Number of training epochs (integer)
    validation_split = 0.0       # Validation data ratio (0.0 = 0%, 1.0 = 100%)
    learning_rate = 0.0001       # Learning rate value (0.0 to 1.0)
    batch_size = 1               # Batch size for training (integer)
    ** How to write params field **
    [TrainingConfig]\nuse_lora = true\nnum_train_epochs = 1\nvalidation_split = 0.0\nlearning_rate = 0.0001\nbatch_size = 1

    \b
    Examples:
        # Interactive mode (will prompt for each field)
        adxp-cli finetuning training create
        
        # Command line mode
        adxp-cli finetuning training create --name "My Training" --dataset-ids "uuid,uuid" --base-model-id "uuid" --trainer-id "uuid" --resource '{"cpu_quota": 4, "mem_quota": 8, "gpu_quota": 1, "gpu_type": "H100"}' --params "learning_rate=0.001\nepochs=10\nbatch_size=32"
        
        # Using JSON file
        adxp-cli finetuning training create --json training_config.json
    """
    if json_path:
        # JSON file style
        with open(json_path, 'r') as f:
            data = json_module.load(f)
        # Backend server bug workaround: Force status and prev_status to "initialized"
        data['status'] = "initialized"
        data['prev_status'] = "initialized"
    else:
        # Parameter style
        try:
            # Parse dataset_ids from comma-separated string
            dataset_ids_list = [id.strip() for id in dataset_ids.split(',')]
            
            # Parse resource from JSON string
            resource_dict = json_module.loads(resource)
            
            data = {
                'name': name,
                'dataset_ids': dataset_ids_list,
                'base_model_id': base_model_id,
                'trainer_id': trainer_id,
                'resource': resource_dict,
                'params': params,
                'description': description
                # Note: status and prev_status are automatically set to "initialized" in the SDK
                # due to backend server bug workaround
            }
        except json_module.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON format in --resource: {e}")
        except Exception as e:
            raise click.ClickException(f"Error parsing parameters: {e}")
    
    result = create_training(data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Created:")

@training.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated training IDs')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, ids, json):
    """List all trainings.
    
    \b
    Examples:
        # Basic listing
        adxp-cli finetuning training list
        
        # With pagination
        adxp-cli finetuning training list --page 2 --size 20
        
        # With filtering and sorting
        adxp-cli finetuning training list --filter "status:trained" --sort "created_at,desc"
        
        # Search by name
        adxp-cli finetuning training list --search "my training"
        
        # Get specific trainings by IDs
        adxp-cli finetuning training list --ids "id1,id2,id3"
        
        # JSON output
        adxp-cli finetuning training list --json
    """
    result = list_trainings(page, size, sort, filter, search, ids)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # Handle both old format (direct array) and new format (data + payload)
        if "data" in result:
            trainings = result["data"]
        else:
            trainings = result
        print_training_list(trainings, title="Training List:")

@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(training_id, json):
    """Get a training by ID.
    
    \b
    Examples:
        # Get training details
        adxp-cli finetuning training get 0c9fd688-783f-4e83-a7a4-cfe2693dec31
        
        # Get training details in JSON format
        adxp-cli finetuning training get 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json
    """
    result = get_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Detail:")

@training.command()
@click.argument('training_id')
@click.option('--name', help='Training name')
@click.option('--status', help='Training status (initialized, starting, training, trained, error, etc.)')
@click.option('--prev-status', help='Previous status')
@click.option('--progress', help='Progress information as JSON string (e.g., {"percentage": 50})')
@click.option('--resource', help='Resource configuration as JSON string (e.g., {"cpu_quota": 4, "mem_quota": 16, "gpu_quota": 1, "gpu_type": "H100"})')
@click.option('--dataset-ids', help='Comma-separated dataset IDs for training')
@click.option('--base-model-id', help='Base model ID for fine-tuning')
@click.option('--params', help='Training parameters as string (e.g., "learning_rate=0.001\\nepochs=10\\nbatch_size=32")')
@click.option('--envs', help='Environment variables as JSON string (e.g., {"CUDA_VISIBLE_DEVICES": "0"})')
@click.option('--description', help='Training description')
@click.option('--project-id', help='Project ID')
@click.option('--task-id', help='Task ID')
@click.option('--trainer-id', help='Trainer ID')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Training update JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def update(training_id, name, status, prev_status, progress, resource, dataset_ids, base_model_id, params, envs, description, project_id, task_id, trainer_id, json_path, json_output):
    """Update a training.
    
    \b
    Examples:
        # Update training name
        adxp-cli finetuning training update 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --name "Updated Training Name"
        
        # Update progress
        adxp-cli finetuning training update 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --progress '{"percentage": 75}'
        
        # Update resource configuration
        adxp-cli finetuning training update 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --resource '{"cpu_quota": 8, "mem_quota": 16, "gpu_quota": 2}'
        
        # Update multiple fields
        adxp-cli finetuning training update 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --name "New Name" --description "Updated description"
        
        # Using JSON file
        adxp-cli finetuning training update 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json update_config.json
    """
    data = {}
    
    if json_path:
        with open(json_path, 'r') as f:
            data = json_module.load(f)
    else:
        # Parse individual options
        if name is not None:
            data['name'] = name
        if status is not None:
            data['status'] = status
        if prev_status is not None:
            data['prev_status'] = prev_status
        if progress is not None:
            try:
                data['progress'] = json_module.loads(progress)
            except json_module.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON format in --progress: {e}")
        if resource is not None:
            try:
                data['resource'] = json_module.loads(resource)
            except json_module.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON format in --resource: {e}")
        if dataset_ids is not None:
            data['dataset_ids'] = [id.strip() for id in dataset_ids.split(',')]
        if base_model_id is not None:
            data['base_model_id'] = base_model_id
        if params is not None:
            data['params'] = params
        if envs is not None:
            try:
                data['envs'] = json_module.loads(envs)
            except json_module.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON format in --envs: {e}")
        if description is not None:
            data['description'] = description
        if project_id is not None:
            data['project_id'] = project_id
        if task_id is not None:
            data['task_id'] = task_id
        if trainer_id is not None:
            data['trainer_id'] = trainer_id
    
    if not data:
        raise click.ClickException("No update data provided. Use individual options or --json file.")
    
    result = update_training(training_id, data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Updated:")

@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(training_id, json):
    """Delete a training by ID.
    
    \b
    Examples:
        # Delete a training
        adxp-cli finetuning training delete 0c9fd688-783f-4e83-a7a4-cfe2693dec31
    """
    result = delete_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("✅ Training deleted successfully", fg="green")

@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def status(training_id, json):
    """Get training status.
    
    \b
    Examples:
        # Get training status
        adxp-cli finetuning training status 0c9fd688-783f-4e83-a7a4-cfe2693dec31
        
        # Get training status in JSON format
        adxp-cli finetuning training status 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json
    """
    result = get_training_status(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Status:")

@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def start(training_id, json):
    """Start a training.
    
    \b
    Examples:
        # Start a training
        adxp-cli finetuning training start 0c9fd688-783f-4e83-a7a4-cfe2693dec31
        
        # Start a training and get JSON response
        adxp-cli finetuning training start 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json
    """
    result = start_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Started:")

@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def stop(training_id, json):
    """Stop a training.
    
    \b
    Examples:
        # Stop a training
        adxp-cli finetuning training stop 0c9fd688-783f-4e83-a7a4-cfe2693dec31
        
        # Stop a training and get JSON response
        adxp-cli finetuning training stop 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json
    """
    result = stop_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Training Stopped:")

# ====================================================================
# Metrics Commands
# ====================================================================

@finetuning.group()
def metrics():
    """Manage training metrics and events."""
    pass

@metrics.command()
@click.argument('training_id')
@click.option('--type', default='train', help='Metric type (train, evaluation, dpo)')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(training_id, type, page, size, json):
    """List training metrics.
    
    \b
    Examples:
        # List training metrics (default: train type)
        adxp-cli finetuning metrics list 0c9fd688-783f-4e83-a7a4-cfe2693dec31
        
        # List evaluation metrics
        adxp-cli finetuning metrics list 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --type evaluation
        
        # List DPO metrics
        adxp-cli finetuning metrics list 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --type dpo
        
        # With pagination
        adxp-cli finetuning metrics list 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --page 2 --size 20
        
        # JSON output
        adxp-cli finetuning metrics list 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json
    """
    result = get_training_metrics(training_id, type=type, page=page, size=size)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # Handle new format (data + payload)
        if "data" in result:
            metrics = result["data"]
        else:
            metrics = result
        print_metrics_list(metrics, title="Training Metrics:")

@metrics.command()
@click.argument('training_id')
@click.option('--after', default=None, help='Get events after this timestamp e.g., "2025-08-26T00:00:00.000Z"')
@click.option('--limit', default=100, help='Maximum number of events to return')
@click.option('--json', is_flag=True, help='Output in JSON format')
def events(training_id, after, limit, json):
    """Get training events.
    
    \b
    Examples:
        # Get events with both timestamp and limit
        adxp-cli finetuning metrics events 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --after "2025-01-10T00:00:00.000Z" --limit 10
        
        # JSON output
        adxp-cli finetuning metrics events 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --after "2025-01-10T00:00:00.000Z" --limit 10 --json
    """
    result = get_training_events(training_id, after=after, limit=limit)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # Handle new format (data + payload)
        if "data" in result:
            events = result["data"]
        else:
            events = result
        print_events_list(events, title="Training Events:")

@metrics.command()
@click.argument('training_id')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Metrics JSON file path')
@click.option('--step', type=int, help='Training step number')
@click.option('--loss', type=float, help='Loss value')
@click.option('--type', default='train', help='Metric type (train, evaluation, dpo)')
@click.option('--custom-metrics', help='Custom metrics as JSON string')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def register(training_id, json_path, step, loss, type, custom_metrics, json_output):
    """Register training metrics.
    
    \b
    Examples:
        # Basic usage with step and loss
        adxp-cli finetuning metrics register 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --step 100 --loss 0.5
        
        # With custom metrics
        adxp-cli finetuning metrics register 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --step 100 --loss 0.5 --custom-metrics '{"accuracy": 0.95, "f1_score": 0.92}'
        
        # Using JSON file
        adxp-cli finetuning metrics register 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --json metrics.json
        
        # Different metric types
        adxp-cli finetuning metrics register 0c9fd688-783f-4e83-a7a4-cfe2693dec31 --step 50 --loss 0.3 --type evaluation
    """
    if json_path:
        with open(json_path, 'r') as f:
            metrics_data = json_module.load(f)
    else:
        if step is None or loss is None:
            raise click.ClickException("--step and --loss are required when not using --json file")
        
        metrics_data = [{
            'step': step,
            'loss': loss,
            'type': type,
            'custom_metric': {}  # Default empty custom metrics
        }]
        
        if custom_metrics:
            try:
                custom_data = json_module.loads(custom_metrics)
                metrics_data[0]['custom_metric'] = custom_data
            except json_module.JSONDecodeError:
                raise click.ClickException("--custom-metrics must be valid JSON")
    
    result = register_training_metrics(training_id, metrics_data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("✅ Metrics registered successfully", fg="green")

# ====================================================================
# Trainer Commands
# ====================================================================

@finetuning.group()
def trainer():
    """Manage finetuning trainers."""
    pass

@trainer.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, json):
    """List all trainers.
    
    \b
    Examples:
        # Basic listing
        adxp-cli finetuning trainer list
        
        # With pagination
        adxp-cli finetuning trainer list --page 2 --size 20
        
        # With filtering and sorting
        adxp-cli finetuning trainer list --sort "created_at,desc"
        
        # Search by description
        adxp-cli finetuning trainer list --search "Hello"
        
        # JSON output
        adxp-cli finetuning trainer list --json
    """
    result = list_trainers(page, size, sort, filter, search)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # Handle new format (data + payload)
        if "data" in result:
            trainers = result["data"]
        else:
            trainers = result
        print_trainer_list(trainers, title="Trainer List:")

@trainer.command()
@click.argument('trainer_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(trainer_id, json):
    """Get a trainer by ID.
    
    \b
    Examples:
        # Get trainer details
        adxp-cli finetuning trainer get 02634dbb-a9cd-4437-83d7-3aab9bb1d3d8-123
        
        # Get trainer details in JSON format
        adxp-cli finetuning trainer get 02634dbb-a9cd-4437-83d7-3aab9bb1d3d8-123 --json
    """
    result = get_trainer(trainer_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_trainer_detail(result, title="🏋️ Trainer Detail:")

@trainer.command()
@click.option('--registry-url', prompt=True, help='Docker image URI in Harbor registry')
@click.option('--default-params', prompt=True, help='Training configuration parameters in TOML format')
@click.option('--description', default='', help='Trainer description')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Trainer creation JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def create(registry_url, default_params, description, json_path, json_output):
    """Create a new trainer.
    
    \b
    Examples:
        # Interactive mode (will prompt for each field)
        adxp-cli finetuning trainer create
        
        # Command line mode
        adxp-cli finetuning trainer create --registry-url "harbor.example.com/project/trainer:latest" --default-params "[TrainingConfig]\nuse_lora = true\nnum_train_epochs = 1\nvalidation_split = 0.0\nlearning_rate = 0.0001\nbatch_size = 1" --description "PyTorch trainer for fine-tuning"
        
        # Using JSON file
        adxp-cli finetuning trainer create --json trainer_config.json
        
        # Create with JSON output
        adxp-cli finetuning trainer create --registry-url "harbor.example.com/project/trainer:latest" --default-params "[TrainingConfig]\nuse_lora = true\nnum_train_epochs = 1\nvalidation_split = 0.4\nlearning_rate = 0.001\nbatch_size = 2" --json-output
    """
    if json_path:
        with open(json_path, 'r') as f:
            data = json_module.load(f)
    else:
        data = {
            'registry_url': registry_url,
            'default_params': default_params,
            'description': description
        }
    
    result = create_trainer(data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_trainer_detail(result, title="🏋️ Trainer Created:")

@trainer.command()
@click.argument('trainer_id')
@click.option('--registry-url', help='Docker image URI in Harbor registry')
@click.option('--default-params', help='Training configuration parameters in TOML format')
@click.option('--description', help='Trainer description')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Trainer update JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def update(trainer_id, registry_url, default_params, description, json_path, json_output):
    """Update a trainer.
    
    \b
    Examples:
        # Update trainer description
        adxp-cli finetuning trainer update trainer-123 --description "Updated PyTorch trainer"
        
        # Update registry URL
        adxp-cli finetuning trainer update trainer-123 --registry-url "harbor.example.com/project/trainer:v2.0"
        
        # Update default parameters
        adxp-cli finetuning trainer update trainer-123 --default-params "[TrainingConfig]\nuse_lora = true\nnum_train_epochs = 1\nvalidation_split = 0.0\nlearning_rate = 0.0001\nbatch_size = 1"
        
        # Update multiple fields
        adxp-cli finetuning trainer update trainer-123 --description "New description" --registry-url "harbor.example.com/project/trainer:v2.0"
        
        # Using JSON file
        adxp-cli finetuning trainer update trainer-123 --json update_config.json
    """
    data = {}
    
    if json_path:
        with open(json_path, 'r') as f:
            data = json_module.load(f)
    else:
        if registry_url is not None:
            data['registry_url'] = registry_url
        if default_params is not None:
            data['default_params'] = default_params
        if description is not None:
            data['description'] = description
    
    if not data:
        raise click.ClickException("No update data provided. Use individual options or --json file.")
    
    result = update_trainer(trainer_id, data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_trainer_detail(result, title="🏋️ Trainer Updated:")

@trainer.command()
@click.argument('trainer_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(trainer_id, json):
    """Delete a trainer by ID.
    
    \b
    Examples:
        # Delete a trainer
        adxp-cli finetuning trainer delete 02634dbb-a9cd-4437-83d7-3aab9bb1d3d8
    """
    result = delete_trainer(trainer_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("✅ Trainer deleted successfully", fg="green")

@click.group()
def cli():
    """AIP Finetuning CLI"""
    pass

cli.add_command(finetuning)

if __name__ == "__main__":
    cli()
