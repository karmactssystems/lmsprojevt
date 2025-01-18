class ModuleDatabaseRouter:
    """
    A router to control database operations for different modules.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'module1':
            return 'default'  # SQLite
        elif model._meta.app_label == 'module2':
            return 'mongo'  # MongoDB
        elif model._meta.app_label == 'module3':
            return 'neo4j'  # Neo4j
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'module1':
            return 'default'  # SQLite
        elif model._meta.app_label == 'module2':
            return 'mongo'  # MongoDB
        elif model._meta.app_label == 'module3':
            return 'neo4j'  # Neo4j
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relationships if both models are in the same database.
        """
        db_set = {'default', 'mongo', 'neo4j'}
        if {obj1._state.db, obj2._state.db} <= db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations only apply to the appropriate database.
        """
        if app_label == 'module1':
            return db == 'default'
        elif app_label == 'module2':
            return db == 'mongo'
        elif app_label == 'module3':
            return db == 'neo4j'
        return None
