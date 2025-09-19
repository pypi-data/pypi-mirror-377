import { IDict, IJCadFormSchemaRegistry } from '@jupytercad/schema';
import formSchema from '@jupytercad/schema/lib/_interface/forms.json';

export class JupyterCadFormSchemaRegistry implements IJCadFormSchemaRegistry {
  constructor() {
    this._registry = new Map<string, IDict>(Object.entries(formSchema));
  }

  registerSchema(name: string, schema: IDict): void {
    if (!this._registry.has(name)) {
      this._registry.set(name, schema);
    } else {
      console.error('Worker is already registered!');
    }
  }

  has(name: string): boolean {
    return this._registry.has(name);
  }

  getSchemas(): Map<string, IDict> {
    return this._registry;
  }

  private _registry: Map<string, IDict>;
}
