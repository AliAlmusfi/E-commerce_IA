from contextvars import ContextVar

WRITE_DB = 'default'
READ_DBS = ['replica']


# Tracks whether the current request must bypass the replica
force_primary_var: ContextVar[bool] = ContextVar("force_primary", default=False)


def set_force_primary(value: bool = True):
    force_primary_var.set(value)


class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        # 1. If the user just wrote data (or is in checkout), read from Primary
        if force_primary_var.get():
            return WRITE_DB
        # 2. Otherwise, offload reads to the replica
        return READ_DBS[0]

    def db_for_write(self, model, **hints):
        return WRITE_DB

    def allow_relation(self, obj1, obj2, **hints):
        # Allow ForeignKeys between objects fetched from default and replica
        db_set = {WRITE_DB, *READ_DBS}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Only run schema migrations on the Primary; MySQL replicates DDL automatically
        return db == WRITE_DB