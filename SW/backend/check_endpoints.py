from routers import student_router, teacher_router, supervisor_router

print("Student router endpoints:")
for route in student_router.router.routes:
    print(route.path, route.methods)

print("\nSupervisor router endpoints:")
for route in supervisor_router.router.routes:
    print(route.path, route.methods)
