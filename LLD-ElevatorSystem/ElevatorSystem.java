package ElevatorSystem;
import java.util.*;

enum Direction {
    UP, DOWN, IDLE
}

// Request class represents a user request for an elevator
class Request {
    private int floor;
    private Direction direction;

    public Request(int floor, Direction direction) {
        this.floor = floor;
        this.direction = direction;
    }

    public int getFloor() {
        return floor;
    }

    public Direction getDirection() {
        return direction;
    }
}

// Elevator class represents an elevator and its behavior
class Elevator {
    private int id;
    private int currentFloor;
    private Direction direction;
    private boolean isMoving;
    private boolean isOverloaded;

    public Elevator(int id) {
        this.id = id;
        this.currentFloor = 0;
        this.direction = Direction.IDLE;
        this.isMoving = false;
        this.isOverloaded = false;
    }

    public void moveToFloor(int floor) {
        System.out.println("Elevator " + id + " moving to floor " + floor);
        this.currentFloor = floor;
        this.direction = Direction.IDLE;
    }

    public void openDoors() {
        System.out.println("Elevator " + id + " doors opening...");
    }

    public void closeDoors() {
        System.out.println("Elevator " + id + " doors closing...");
    }

    public void stopElevator() {
        System.out.println("Elevator " + id + " stopping...");
        this.direction = Direction.IDLE;
    }

    public int getCurrentFloor() {
        return currentFloor;
    }

    public Direction getDirection() {
        return direction;
    }

    public boolean isOverloaded() {
        return isOverloaded;
    }
}

// ElevatorController manages all the elevators in the building
class ElevatorController {
    private List<Elevator> elevators;

    public ElevatorController(int elevatorCount) {
        elevators = new ArrayList<>();
        for (int i = 0; i < elevatorCount; i++) {
            elevators.add(new Elevator(i + 1));
        }
    }

    public void requestElevator(Request request) {
        Elevator assignedElevator = getNearestAvailableElevator(request);
        if (assignedElevator != null) {
            assignedElevator.moveToFloor(request.getFloor());
            assignedElevator.openDoors();
            assignedElevator.closeDoors();
        } else {
            System.out.println("No elevators available currently.");
        }
    }

    private Elevator getNearestAvailableElevator(Request request) {
        Elevator nearest = null;
        int minDistance = Integer.MAX_VALUE;

        for (Elevator elevator : elevators) {
            int distance = Math.abs(elevator.getCurrentFloor() - request.getFloor());
            if (distance < minDistance) {
                minDistance = distance;
                nearest = elevator;
            }
        }
        return nearest;
    }
}

// BuildingFloor represents each floor in the building
class BuildingFloor {
    private int floorNo;
    private boolean upButton;
    private boolean downButton;
    private ElevatorController controller;

    public BuildingFloor(int floorNo, ElevatorController controller) {
        this.floorNo = floorNo;
        this.controller = controller;
        this.upButton = false;
        this.downButton = false;
    }

    public void upRequest() {
        System.out.println("Up request from floor " + floorNo);
        Request request = new Request(floorNo, Direction.UP);
        controller.requestElevator(request);
    }

    public void downRequest() {
        System.out.println("Down request from floor " + floorNo);
        Request request = new Request(floorNo, Direction.DOWN);
        controller.requestElevator(request);
    }
}

// Main class to test the elevator system
public class ElevatorSystem {
    public static void main(String[] args) {
        ElevatorController controller = new ElevatorController(5);
        BuildingFloor floor3 = new BuildingFloor(3, controller);
        BuildingFloor floor5 = new BuildingFloor(5, controller);

        floor3.upRequest();  // Request an elevator from floor 3 going up
        floor5.downRequest(); // Request an elevator from floor 5 going down
    }
}
