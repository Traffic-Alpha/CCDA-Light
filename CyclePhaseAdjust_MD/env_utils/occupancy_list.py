'''
@Author: WANG Maonan
@Date: 2024-05-01 18:04:46
@Description: 占有率的统计指标
@LastEditTime: 2024-05-01 18:25:50
'''
import numpy as np

class OccupancyList:
    def __init__(self) -> None:
        self.occupancies = []

    def add_occupancy(self, occupancy: list) -> None:
        """
        Add a list of occupancy data to the list.

        Parameters:
        occupancy (list): A list of floats representing the occupancy for each road.

        Raises:
        ValueError: If the input is not a list of floats.

        Example:
        add_occupancy([0.5, 0.7, 0.9])  # Adds this list of occupancies
        """
        if not isinstance(occupancy, list) or not all(isinstance(e, float) for e in occupancy):
            raise ValueError("Occupancy must be a list of floats.")
        self.occupancies.append(occupancy)
        
    def calculate_statistics(self) -> dict:
        """
        Calculate and return statistical measures for the stored occupancy data.

        Returns:
        dict: A dictionary containing the average, max, min, standard deviation, and median of the occupancy data.

        Example:
        calculate_statistics()  # Returns {'average': ..., 'max': ..., 'min': ..., 'std_dev': ..., 'median': ...}
        """
        if not self.occupancies:
            return {}
        
        occupancy_array = np.array(self.occupancies, dtype=np.float32)
        return {
            'average': np.mean(occupancy_array, axis=0) / 100,
            'max': np.max(occupancy_array, axis=0) / 100,
            'min': np.min(occupancy_array, axis=0) / 100,
            'std_dev': np.std(occupancy_array, axis=0) / 100,
            'median': np.median(occupancy_array, axis=0) / 100
        }

    def reset_occupancies(self) -> None:
        """
        Reset the stored occupancy data.

        Example:
        reset_occupancies()  # Clears all stored occupancy data
        """
        self.occupancies.clear()
