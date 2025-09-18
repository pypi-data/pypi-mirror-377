from typing import Any

from aiware.processing import Engine, Dag, JOB_TARGET, parallel, output_writer, ExecutionPreferences

aiware: Any = ...

extract_text = Engine(id="engine-1")
embed = Engine(id="engine-2")

# dag = Dag()


# dag = (extract_text(JOB_TARGET, payload={ "enable_hybrid_chunker": True })
#     .then(parallel(     # maybe use unix and/or/; semantics instead
#         output_writer,
#         embed.then(output_writer)
#     ))
#     .build_dag())

# job = aiware.createJob(name="", input=dag)

# async/await?
